from database import SessionLocal
from models import Transaction

from investigation import investigate_payment
from intervention_engine import choose_intervention
from erv_engine import calculate_expected_recovery_value
from policy_engine import check_policy
from action_executor import execute_action

from recovery_tracking import (
    can_attempt_recovery,
    record_recovery_attempt
)

from recovery_state_machine import (
    get_initial_state,
    update_state
)

from recovery_log import get_recovery_history, save_recovery_log


# =========================================================
# RECOVERY AGENT
# =========================================================

def run_recovery_agent(transaction_id: str):

    db = SessionLocal()

    try:

        transaction = (
            db.query(Transaction)
            .filter(
                Transaction.transaction_id == transaction_id
            )
            .first()
        )

        if not transaction:

            return {
                "transaction_id": transaction_id,
                "final_status": "NOT_FOUND",
                "amount_recovered": 0,
                "message": "Transaction not found."
            }

        customer = getattr(
            transaction,
            "customer",
            None
        )

        customer_data = {
            "customer_id": getattr(
                customer,
                "customer_id",
                getattr(
                    transaction,
                    "customer_id",
                    None
                )
            ),

            "name": getattr(
                customer,
                "name",
                "Unknown"
            ),

            "email": getattr(
                customer,
                "email",
                ""
            )
        }

        amount = float(
            transaction.amount or 0
        )

        payment_method = (
            transaction.payment_method
            or "UNKNOWN"
        )

        failure_reason = (
            transaction.failure_reason
        )

        payment_status = str(
            transaction.status
        ).upper()

        retry_count = int(
            getattr(
                transaction,
                "retry_count",
                0
            )
            or 0
        )

    finally:

        db.close()


    # =========================================================
    # STATE MACHINE
    # =========================================================

    current_state = get_initial_state()

    state_history = [
        current_state
    ]


    def transition(next_state):

        nonlocal current_state

        current_state = update_state(
            current_state,
            next_state
        )

        state_history.append(
            current_state
        )


    # =========================================================
    # ALREADY RECOVERED
    # =========================================================

    if payment_status in [
        "SUCCESS",
        "RECOVERED"
    ]:

        transition("INVESTIGATING")
        transition("EVALUATING")
        transition("POLICY_CHECK")
        transition("STOPPED")

        return {
            "transaction_id": transaction_id,
            "customer": customer_data,
            "status": "ALREADY_RECOVERED",
            "message": (
                "Recovery stopped because this "
                "transaction was already recovered."
            ),
            "final_status": "RECOVERED",
            "amount": amount,
            "amount_recovered": amount,
            "recovery_probability": 0,
            "expected_recovery_value": 0,
            "action": None,
            "policy": {
                "approved": False,
                "decision": "STOP",
                "reason": (
                    "Transaction is already successful."
                )
            },
            "state_history": state_history
        }


    # =========================================================
    # ALREADY PENDING
    # =========================================================

    if payment_status in [
        "PAYMENT_PENDING",
        "PENDING"
    ]:

        transition("INVESTIGATING")
        transition("EVALUATING")
        transition("POLICY_CHECK")
        transition("STOPPED")

        return {
            "transaction_id": transaction_id,
            "customer": customer_data,
            "status": "RECOVERY_ALREADY_PENDING",
            "message": (
                "Recovery stopped because a previous "
                "recovery action is already pending."
            ),
            "final_status": "PAYMENT_PENDING",
            "amount": amount,
            "amount_recovered": 0,
            "recovery_probability": 0,
            "expected_recovery_value": 0,
            "action": None,
            "policy": {
                "approved": False,
                "decision": "STOP",
                "reason": (
                    "Transaction is already "
                    "in PAYMENT_PENDING state."
                )
            },
            "state_history": state_history
        }


    # =========================================================
    # PREVIOUS TERMINAL ATTEMPT
    # =========================================================

    recovery_history = get_recovery_history(
        transaction_id
    )

    latest_log = (
        recovery_history[0]
        if recovery_history
        else None
    )


    if latest_log:

        latest_status = str(
            latest_log.get(
                "final_status",
                ""
            )
        ).upper()

        if latest_status in [
            "RECOVERY_FAILED",
            "STOPPED",
            "STOP",
            "BLOCK",
            "ESCALATE"
        ]:

            transition("INVESTIGATING")
            transition("EVALUATING")
            transition("POLICY_CHECK")
            transition("STOPPED")

            return {
                "transaction_id": transaction_id,
                "customer": customer_data,
                "amount": amount,

                "recovery_probability": float(
                    latest_log.get(
                        "recovery_probability",
                        0
                    ) or 0
                ),

                "expected_recovery_value": float(
                    latest_log.get(
                        "expected_recovery_value",
                        0
                    ) or 0
                ),

                "action": latest_log.get(
                    "action"
                ),

                "policy": {
                    "approved": False,
                    "decision": "STOP",
                    "reason": (
                        "Recovery stopped because the "
                        "previous recovery attempt already "
                        "reached a terminal state: "
                        f"{latest_status}."
                    )
                },

                "tracking": {
                    "allowed": False,
                    "reason": (
                        "Duplicate recovery attempt blocked."
                    )
                },

                "final_status": latest_status,

                "amount_recovered": float(
                    latest_log.get(
                        "amount_recovered",
                        0
                    ) or 0
                ),

                "state_history": state_history
            }


    # =========================================================
    # INVESTIGATION
    # =========================================================

    transition("INVESTIGATING")

    investigation = investigate_payment(
        transaction_id
    )


    if not investigation or "error" in investigation:

        transition("STOPPED")

        return {
            "transaction_id": transaction_id,
            "customer": customer_data,
            "final_status": "STOPPED",
            "amount": amount,
            "amount_recovered": 0,
            "message": (
                investigation.get(
                    "error",
                    "Investigation failed."
                )
                if investigation
                else "Investigation failed."
            ),
            "state_history": state_history
        }


    # =========================================================
    # EVALUATING
    # =========================================================

    transition("EVALUATING")

    recovery_probability = float(
        investigation.get(
            "recovery_probability",
            0
        ) or 0
    )


    # =========================================================
    # ERV
    # =========================================================

    erv_result = (
        calculate_expected_recovery_value(
            amount=amount,
            recovery_probability=recovery_probability,
            action_cost=20
        )
    )

    expected_recovery_value = float(
        erv_result.get(
            "expected_recovery_value",
            0
        ) or 0
    )


    # =========================================================
    # INTERVENTION
    # =========================================================

    intervention = choose_intervention(
        failure_reason=failure_reason,
        recovery_probability=recovery_probability,
        expected_recovery_value=expected_recovery_value,
        amount=amount
    )

    action = intervention.get(
        "action"
    )


    # =========================================================
    # POLICY CHECK
    # =========================================================

    transition("POLICY_CHECK")


    # ---------------------------------------------------------
    # STOP / ESCALATE FROM INTERVENTION
    # ---------------------------------------------------------

    if not action:

        transition("STOPPED")

        return {
            "transaction_id": transaction_id,
            "customer": customer_data,
            "amount": amount,
            "recovery_probability": recovery_probability,
            "expected_recovery_value": expected_recovery_value,
            "action": None,
            "intervention": intervention,
            "policy": {
                "approved": False,
                "decision": "STOP",
                "reason": (
                    "No recovery action was selected."
                )
            },
            "final_status": "STOPPED",
            "amount_recovered": 0,
            "state_history": state_history
        }


    # =========================================================
    # TRACKING CHECK
    # =========================================================

    tracking = can_attempt_recovery(
        transaction_id=transaction_id,
        action=action
    )


    if not tracking.get(
        "allowed",
        False
    ):

        transition("STOPPED")

        return {
            "transaction_id": transaction_id,
            "customer": customer_data,
            "amount": amount,
            "recovery_probability": recovery_probability,
            "expected_recovery_value": expected_recovery_value,
            "action": action,
            "intervention": intervention,
            "final_status": "STOPPED",
            "amount_recovered": 0,
            "policy": {
                "approved": False,
                "decision": "STOP",
                "reason": tracking.get(
                    "reason",
                    "Recovery attempt blocked."
                )
            },
            "tracking": tracking,
            "state_history": state_history
        }


    # =========================================================
    # POLICY ENGINE
    # =========================================================

    policy = check_policy(
        action=action,
        amount=amount,
        recovery_probability=recovery_probability,
        expected_recovery_value=expected_recovery_value,
        retry_count=retry_count,
        payment_status=payment_status,
        failure_reason=failure_reason
    )


    # =========================================================
    # POLICY REJECTED
    # =========================================================

    if not policy.get(
        "approved",
        False
    ):

        decision = str(
            policy.get(
                "decision",
                "STOP"
            )
        ).upper()


        if decision == "ESCALATE":

            transition("ESCALATED")

            save_recovery_log(
                transaction_id=transaction_id,
                action=action,
                recovery_probability=recovery_probability,
                expected_recovery_value=expected_recovery_value,
                policy_decision="ESCALATE",
                execution_status="NOT_EXECUTED",
                verification_status="NOT_VERIFIED",
                final_status="ESCALATE",
                amount_recovered=0
            )

            return {
                "transaction_id": transaction_id,
                "customer": customer_data,
                "amount": amount,
                "recovery_probability": recovery_probability,
                "expected_recovery_value": expected_recovery_value,
                "action": action,
                "intervention": intervention,
                "policy": policy,
                "tracking": tracking,
                "final_status": "ESCALATE",
                "amount_recovered": 0,
                "state_history": state_history
            }


        transition("STOPPED")

        save_recovery_log(
            transaction_id=transaction_id,
            action=action,
            recovery_probability=recovery_probability,
            expected_recovery_value=expected_recovery_value,
            policy_decision="STOP",
            execution_status="NOT_EXECUTED",
            verification_status="NOT_VERIFIED",
            final_status="STOPPED",
            amount_recovered=0
        )

        return {
            "transaction_id": transaction_id,
            "customer": customer_data,
            "amount": amount,
            "recovery_probability": recovery_probability,
            "expected_recovery_value": expected_recovery_value,
            "action": action,
            "intervention": intervention,
            "policy": policy,
            "tracking": tracking,
            "final_status": "STOPPED",
            "amount_recovered": 0,
            "state_history": state_history
        }


    # =========================================================
    # RECORD ATTEMPT
    # =========================================================

    tracking_result = record_recovery_attempt(
        transaction_id=transaction_id,
        action=action
    )


    # =========================================================
    # EXECUTING
    # =========================================================

    transition("EXECUTING")


    execution = execute_action(
        action=action,
        transaction_id=transaction_id,
        amount=amount,
        payment_method=payment_method
    )


    execution_status = str(
        execution.get(
            "execution_status",
            execution.get(
                "status",
                "FAILED"
            )
        )
    ).upper()


    payment_attempted = bool(
        execution.get(
            "payment_attempted",
            False
        )
    )


    payment_recovered = bool(
        execution.get(
            "payment_recovered",
            False
        )
    )


    # =========================================================
    # VERIFYING
    # =========================================================

    transition("VERIFYING")


    # ---------------------------------------------------------
    # RECOVERED
    # ---------------------------------------------------------

    if (
        payment_recovered
        or execution_status in [
            "RECOVERED",
            "SUCCESS",
            "PAYMENT_SUCCESS"
        ]
    ):

        verification_status = "RECOVERED"

        payment_successful = True


    # ---------------------------------------------------------
    # PENDING
    # ---------------------------------------------------------

    elif execution_status in [
        "PAYMENT_PENDING",
        "PENDING"
    ]:

        verification_status = "PAYMENT_PENDING"

        payment_successful = False


    # ---------------------------------------------------------
    # PAYMENT ATTEMPT FAILED
    # ---------------------------------------------------------

    elif payment_attempted:

        verification_status = "RECOVERY_FAILED"

        payment_successful = False


    # ---------------------------------------------------------
    # EXECUTION FAILED
    # ---------------------------------------------------------

    else:

        verification_status = "RECOVERY_FAILED"

        payment_successful = False


    # =========================================================
    # VERIFICATION RESULT
    # =========================================================

    verification = {

        "transaction_id":
            transaction_id,

        "action":
            action,

        "status":
            verification_status,

        "payment_successful":
            payment_successful,

        "message":

            (
                "Payment recovery verified successfully."
                if verification_status == "RECOVERED"

                else
                (
                    "Recovery action executed. "
                    "Payment is awaiting customer action."
                    if verification_status ==
                    "PAYMENT_PENDING"

                    else
                    "Payment recovery could not be verified."
                )
            )
    }


    # =========================================================
    # FINAL STATUS: RECOVERED
    # =========================================================

    if verification_status == "RECOVERED":

        db = SessionLocal()

        try:

            transaction = (
                db.query(Transaction)
                .filter(
                    Transaction.transaction_id ==
                    transaction_id
                )
                .first()
            )

            if transaction:

                transaction.status = "RECOVERED"

            db.commit()

        finally:

            db.close()


        transition("RECOVERED")

        save_recovery_log(
            transaction_id=transaction_id,
            action=action,
            recovery_probability=recovery_probability,
            expected_recovery_value=expected_recovery_value,
            policy_decision=policy.get("decision", "APPROVE"),
            execution_status=execution_status,
            verification_status=verification_status,
            final_status="RECOVERED",
            amount_recovered=amount
        )

        return {
            "transaction_id": transaction_id,
            "customer": customer_data,
            "amount": amount,
            "recovery_probability": recovery_probability,
            "expected_recovery_value": expected_recovery_value,
            "erv": erv_result,
            "action": action,
            "intervention": intervention,
            "policy": policy,
            "tracking": tracking_result,
            "execution": execution,
            "verification": verification,
            "final_status": "RECOVERED",
            "amount_recovered": amount,
            "state_history": state_history
        }


    # =========================================================
    # FINAL STATUS: PAYMENT PENDING
    # =========================================================

    if verification_status == "PAYMENT_PENDING":

        db = SessionLocal()

        try:

            transaction = (
                db.query(Transaction)
                .filter(
                    Transaction.transaction_id ==
                    transaction_id
                )
                .first()
            )

            if transaction:

                transaction.status = (
                    "PAYMENT_PENDING"
                )

            db.commit()

        finally:

            db.close()


        save_recovery_log(
            transaction_id=transaction_id,
            action=action,
            recovery_probability=recovery_probability,
            expected_recovery_value=expected_recovery_value,
            policy_decision=policy.get("decision", "APPROVE"),
            execution_status=execution_status,
            verification_status=verification_status,
            final_status="PAYMENT_PENDING",
            amount_recovered=0
        )

        return {
            "transaction_id": transaction_id,
            "customer": customer_data,
            "amount": amount,
            "recovery_probability": recovery_probability,
            "expected_recovery_value": expected_recovery_value,
            "erv": erv_result,
            "action": action,
            "intervention": intervention,
            "policy": policy,
            "tracking": tracking_result,
            "execution": execution,
            "verification": verification,
            "final_status": "PAYMENT_PENDING",
            "amount_recovered": 0,
            "state_history": state_history
        }


    # =========================================================
    # FINAL STATUS: RECOVERY FAILED
    # =========================================================

    transition("RECOVERY_FAILED")

    save_recovery_log(
        transaction_id=transaction_id,
        action=action,
        recovery_probability=recovery_probability,
        expected_recovery_value=expected_recovery_value,
        policy_decision=policy.get("decision", "APPROVE"),
        execution_status=execution_status,
        verification_status=verification_status,
        final_status="RECOVERY_FAILED",
        amount_recovered=0
    )

    return {
        "transaction_id": transaction_id,
        "customer": customer_data,
        "amount": amount,
        "recovery_probability": recovery_probability,
        "expected_recovery_value": expected_recovery_value,
        "erv": erv_result,
        "action": action,
        "intervention": intervention,
        "policy": policy,
        "tracking": tracking_result,
        "execution": execution,
        "verification": verification,
        "final_status": "RECOVERY_FAILED",
        "amount_recovered": 0,
        "state_history": state_history
    }