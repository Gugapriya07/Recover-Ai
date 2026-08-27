from datetime import datetime

from database import SessionLocal
from models import Customer, Transaction, RecoveryLog


# ============================================================
# CONFIGURATION
# ============================================================

MAX_RETRIES = 3
AUTONOMOUS_RECOVERY_LIMIT = 10000
ACTION_COST = 20


# ============================================================
# INVESTIGATION
# ============================================================

def investigate_payment(transaction_id):

    db = SessionLocal()

    try:

        transaction = (
            db.query(Transaction)
            .filter(Transaction.transaction_id == transaction_id)
            .first()
        )

        if not transaction:
            return {
                "error": "Transaction not found"
            }

        customer = (
            db.query(Customer)
            .filter(
                Customer.customer_id == transaction.customer_id
            )
            .first()
        )

        customer_transactions = (
            db.query(Transaction)
            .filter(
                Transaction.customer_id == transaction.customer_id
            )
            .all()
        )

        previous_successes = [
            t for t in customer_transactions
            if t.status == "SUCCESS"
            and t.transaction_id != transaction.transaction_id
        ]

        previous_failures = [
            t for t in customer_transactions
            if t.status == "FAILED"
            and t.transaction_id != transaction.transaction_id
        ]

        total_transactions = len(customer_transactions)

        successful_count = len([
            t for t in customer_transactions
            if t.status == "SUCCESS"
        ])

        success_rate = (
            successful_count / total_transactions * 100
            if total_transactions > 0
            else 0
        )

        failure_reason = transaction.failure_reason

        # ----------------------------------------------------
        # Recovery probability
        # ----------------------------------------------------

        if failure_reason == "INSUFFICIENT_FUNDS":

            recommendation = "WAIT_AND_RETRY"
            recoverability = "HIGH"
            recovery_probability = 60

        elif failure_reason == "UPI_TIMEOUT":

            recommendation = "RETRY_PAYMENT"
            recoverability = "HIGH"
            recovery_probability = 70

        elif failure_reason == "CARD_EXPIRED":

            recommendation = "REQUEST_NEW_PAYMENT_METHOD"
            recoverability = "MEDIUM"
            recovery_probability = 40

        elif failure_reason == "AUTHENTICATION_FAILED":

            recommendation = "REQUEST_REAUTHENTICATION"
            recoverability = "MEDIUM"
            recovery_probability = 35

        elif failure_reason == "BANK_DECLINED":

            recommendation = "TRY_ALTERNATIVE_PAYMENT"
            recoverability = "MEDIUM"
            recovery_probability = 30

        else:

            recommendation = "ESCALATE"
            recoverability = "LOW"
            recovery_probability = 10

        return {
            "transaction": {
                "transaction_id": transaction.transaction_id,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "payment_method": transaction.payment_method,
                "status": transaction.status,
                "failure_reason": transaction.failure_reason
            },

            "customer": {
                "customer_id": customer.customer_id if customer else None,
                "name": customer.name if customer else None,
                "email": customer.email if customer else None
            },

            "customer_history": {
                "total_transactions": total_transactions,
                "successful_transactions": len(previous_successes),
                "failed_transactions": len(previous_failures),
                "success_rate": round(success_rate, 2)
            },

            "investigation": {
                "recoverability": recoverability,
                "recovery_probability": recovery_probability,
                "recommendation": recommendation,
                "reason": (
                    f"Payment failed because of {failure_reason}. "
                    f"Customer has a {round(success_rate, 2)}% "
                    f"historical success rate."
                )
            },

            "recovery_probability": recovery_probability
        }

    finally:

        db.close()


# ============================================================
# EXPECTED RECOVERY VALUE
# ============================================================

def calculate_expected_recovery_value(
    amount,
    recovery_probability
):

    expected_recovery = (
        amount * recovery_probability / 100
    )

    expected_recovery_value = (
        expected_recovery - ACTION_COST
    )

    return {
        "payment_amount": amount,
        "recovery_probability": recovery_probability,
        "expected_recovery": round(expected_recovery, 2),
        "action_cost": ACTION_COST,
        "expected_recovery_value": round(
            expected_recovery_value,
            2
        )
    }


# ============================================================
# INTERVENTION DECISION
# ============================================================

def choose_intervention(
    failure_reason,
    recovery_probability,
    expected_recovery_value,
    amount
):

    # Very low probability
    if recovery_probability < 20:

        return {
            "action": "STOP",
            "priority": "LOW",
            "reason": "Recovery probability is too low."
        }

    # Very low economic value
    if expected_recovery_value < 100:

        return {
            "action": "STOP",
            "priority": "LOW",
            "reason": "Expected recovery value is too low."
        }

    # --------------------------------------------------------
    # INSUFFICIENT FUNDS
    # --------------------------------------------------------

    if failure_reason == "INSUFFICIENT_FUNDS":

        if recovery_probability >= 70:

            return {
                "action": "WAIT_AND_RETRY",
                "priority": "HIGH",
                "reason": (
                    "High recovery probability for insufficient funds. "
                    "Waiting before retry may improve recovery."
                )
            }

        return {
            "action": "SEND_PAYMENT_REMINDER",
            "priority": "MEDIUM",
            "reason": (
                "Customer may need to replenish funds before another attempt."
            )
        }

    # --------------------------------------------------------
    # UPI TIMEOUT
    # --------------------------------------------------------

    if failure_reason == "UPI_TIMEOUT":

        if recovery_probability >= 60:

            return {
                "action": "RETRY_PAYMENT",
                "priority": "HIGH",
                "reason": (
                    "Temporary UPI failure with good recovery probability."
                )
            }

        return {
            "action": "WAIT_AND_RETRY",
            "priority": "MEDIUM",
            "reason": "UPI failure may be temporary."
        }

    # --------------------------------------------------------
    # CARD EXPIRED
    # --------------------------------------------------------

    if failure_reason == "CARD_EXPIRED":

        return {
            "action": "REQUEST_NEW_PAYMENT_METHOD",
            "priority": "HIGH",
            "reason": (
                "The current card cannot be successfully retried."
            )
        }

    # --------------------------------------------------------
    # AUTHENTICATION FAILED
    # --------------------------------------------------------

    if failure_reason == "AUTHENTICATION_FAILED":

        if recovery_probability >= 60:

            return {
                "action": "REQUEST_REAUTHENTICATION",
                "priority": "HIGH",
                "reason": (
                    "Authentication issue may be resolved by reauthentication."
                )
            }

        return {
            "action": "REQUEST_NEW_PAYMENT_METHOD",
            "priority": "MEDIUM",
            "reason": (
                "Authentication failure has limited recovery confidence."
            )
        }

    # --------------------------------------------------------
    # BANK DECLINED
    # --------------------------------------------------------

    if failure_reason == "BANK_DECLINED":

        if recovery_probability >= 60:

            return {
                "action": "TRY_ALTERNATIVE_PAYMENT",
                "priority": "HIGH",
                "reason": (
                    "Bank declined the payment. An alternative payment "
                    "method may recover the transaction."
                )
            }

        return {
            "action": "ESCALATE",
            "priority": "MEDIUM",
            "reason": (
                "Bank decline has uncertain recovery prospects."
            )
        }

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return {
        "action": "ESCALATE",
        "priority": "MEDIUM",
        "reason": (
            "Unknown payment failure requires investigation."
        )
    }


# ============================================================
# POLICY CHECK
# ============================================================

def check_policy(
    transaction_id,
    action,
    amount,
    retry_count
):

    # --------------------------------------------------------
    # Already recovered
    # --------------------------------------------------------

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
                "approved": False,
                "decision": "BLOCK",
                "reason": "Transaction not found."
            }

        if transaction.status == "SUCCESS":

            return {
                "approved": False,
                "decision": "RECOVERED",
                "reason": (
                    "Transaction has already been successfully recovered."
                )
            }

    finally:

        db.close()

    # --------------------------------------------------------
    # Autonomous recovery amount limit
    # --------------------------------------------------------

    autonomous_actions = {
        "RETRY_PAYMENT",
        "WAIT_AND_RETRY",
        "SEND_PAYMENT_REMINDER",
        "TRY_ALTERNATIVE_PAYMENT",
        "REQUEST_NEW_PAYMENT_METHOD",
        "REQUEST_REAUTHENTICATION"
    }

    if (
        amount > AUTONOMOUS_RECOVERY_LIMIT
        and action in autonomous_actions
    ):

        return {
            "approved": False,
            "decision": "ESCALATE",
            "reason": (
                "Transaction amount exceeds the autonomous recovery "
                "limit. Manual review required."
            )
        }

    # --------------------------------------------------------
    # Retry limit
    # --------------------------------------------------------

    retry_actions = {
        "RETRY_PAYMENT",
        "WAIT_AND_RETRY",
        "TRY_ALTERNATIVE_PAYMENT"
    }

    if action in retry_actions:

        if retry_count >= MAX_RETRIES:

            return {
                "approved": False,
                "decision": "ESCALATE",
                "reason": (
                    f"Maximum retry limit of {MAX_RETRIES} "
                    "has been reached."
                )
            }

    # --------------------------------------------------------
    # Stop
    # --------------------------------------------------------

    if action == "STOP":

        return {
            "approved": False,
            "decision": "STOP",
            "reason": (
                "Recovery action stopped because recovery "
                "conditions were not favorable."
            )
        }

    # --------------------------------------------------------
    # Escalation
    # --------------------------------------------------------

    if action == "ESCALATE":

        return {
            "approved": True,
            "decision": "ESCALATE",
            "reason": (
                "Recovery requires manual intervention."
            )
        }

    # --------------------------------------------------------
    # Approved
    # --------------------------------------------------------

    return {
        "approved": True,
        "decision": "APPROVE",
        "reason": "All recovery policies passed."
    }


# ============================================================
# TRACKING
# ============================================================

def record_recovery_attempt(
    transaction_id,
    action
):

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
                "recorded": False,
                "reason": "Transaction not found."
            }

        retry_actions = {
            "RETRY_PAYMENT",
            "WAIT_AND_RETRY",
            "TRY_ALTERNATIVE_PAYMENT"
        }

        if action in retry_actions:

            transaction.retry_count = (
                transaction.retry_count or 0
            ) + 1

        db.commit()

        return {
            "recorded": True,
            "transaction_id": transaction_id,
            "action": action,
            "retry_count": transaction.retry_count or 0
        }

    finally:

        db.close()


# ============================================================
# EXECUTION
# ============================================================

def execute_action(
    action,
    transaction_id,
    amount,
    payment_method
):

    timestamp = datetime.utcnow().isoformat()

    # --------------------------------------------------------
    # RETRY PAYMENT
    # --------------------------------------------------------

    if action == "RETRY_PAYMENT":

        return {
            "transaction_id": transaction_id,
            "action": action,
            "status": "EXECUTED",
            "execution_successful": True,
            "payment_attempted": True,
            "message": (
                f"Simulated payment retry initiated for "
                f"₹{amount} using {payment_method}."
            ),
            "timestamp": timestamp
        }

    # --------------------------------------------------------
    # WAIT AND RETRY
    # --------------------------------------------------------

    if action == "WAIT_AND_RETRY":

        return {
            "transaction_id": transaction_id,
            "action": action,
            "status": "SCHEDULED",
            "execution_successful": True,
            "payment_attempted": False,
            "message": (
                "Payment retry has been scheduled for a later time."
            ),
            "timestamp": timestamp
        }

    # --------------------------------------------------------
    # PAYMENT REMINDER
    # --------------------------------------------------------

    if action == "SEND_PAYMENT_REMINDER":

        return {
            "transaction_id": transaction_id,
            "action": action,
            "status": "EXECUTED",
            "execution_successful": True,
            "payment_attempted": False,
            "message": (
                "Simulated payment reminder sent to the customer."
            ),
            "timestamp": timestamp
        }

    # --------------------------------------------------------
    # ALTERNATIVE PAYMENT
    # --------------------------------------------------------

    if action == "TRY_ALTERNATIVE_PAYMENT":

        return {
            "transaction_id": transaction_id,
            "action": action,
            "status": "EXECUTED",
            "execution_successful": True,
            "payment_attempted": True,
            "message": (
                "Simulated alternative payment method initiated."
            ),
            "timestamp": timestamp
        }

    # --------------------------------------------------------
    # NEW PAYMENT METHOD
    # --------------------------------------------------------

    if action == "REQUEST_NEW_PAYMENT_METHOD":

        return {
            "transaction_id": transaction_id,
            "action": action,
            "status": "EXECUTED",
            "execution_successful": True,
            "payment_attempted": False,
            "message": (
                "Simulated request for a new payment method."
            ),
            "timestamp": timestamp
        }

    # --------------------------------------------------------
    # REAUTHENTICATION
    # --------------------------------------------------------

    if action == "REQUEST_REAUTHENTICATION":

        return {
            "transaction_id": transaction_id,
            "action": action,
            "status": "EXECUTED",
            "execution_successful": True,
            "payment_attempted": False,
            "message": (
                "Simulated customer reauthentication request."
            ),
            "timestamp": timestamp
        }

    # --------------------------------------------------------
    # ESCALATE
    # --------------------------------------------------------

    if action == "ESCALATE":

        return {
            "transaction_id": transaction_id,
            "action": action,
            "status": "ESCALATED",
            "execution_successful": True,
            "payment_attempted": False,
            "message": (
                "Transaction has been escalated for manual review."
            ),
            "timestamp": timestamp
        }

    # --------------------------------------------------------
    # STOP
    # --------------------------------------------------------

    if action == "STOP":

        return {
            "transaction_id": transaction_id,
            "action": action,
            "status": "STOPPED",
            "execution_successful": True,
            "payment_attempted": False,
            "message": (
                "Recovery process stopped according to policy."
            ),
            "timestamp": timestamp
        }

    return {
        "transaction_id": transaction_id,
        "action": action,
        "status": "REJECTED",
        "execution_successful": False,
        "payment_attempted": False,
        "message": "Unknown recovery action.",
        "timestamp": timestamp
    }


# ============================================================
# VERIFICATION
# ============================================================

def verify_recovery(
    transaction_id,
    action,
    failure_reason,
    payment_attempted
):

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
                "action": action,
                "status": "FAILED",
                "payment_successful": False,
                "message": "Transaction not found."
            }

        # ----------------------------------------------------
        # Already successful
        # ----------------------------------------------------

        if transaction.status == "SUCCESS":

            return {
                "transaction_id": transaction_id,
                "action": action,
                "status": "RECOVERED",
                "payment_successful": True,
                "message": (
                    "Payment gateway verification confirmed "
                    "successful recovery."
                )
            }

        # ----------------------------------------------------
        # Simulated successful recovery
        #
        # Current demo scenario:
        # UPI_TIMEOUT + RETRY_PAYMENT
        # ----------------------------------------------------

        if (
            action == "RETRY_PAYMENT"
            and failure_reason == "UPI_TIMEOUT"
            and payment_attempted
        ):

            transaction.status = "SUCCESS"

            db.commit()

            return {
                "transaction_id": transaction_id,
                "action": action,
                "status": "RECOVERED",
                "payment_successful": True,
                "message": (
                    "Payment gateway verification confirmed "
                    "successful recovery."
                )
            }

        # ----------------------------------------------------
        # Other actions remain pending
        # ----------------------------------------------------

        return {
            "transaction_id": transaction_id,
            "action": action,
            "status": "PENDING",
            "payment_successful": False,
            "message": (
                "Recovery action was executed, but payment "
                "has not yet been completed."
            )
        }

    finally:

        db.close()


# ============================================================
# RECOVERY LOG
# ============================================================

def log_recovery_decision(
    transaction_id,
    action,
    probability,
    erv,
    policy_decision,
    execution_status,
    verification_status,
    final_status,
    amount_recovered=0
):

    db = SessionLocal()

    try:

        log = RecoveryLog(
            transaction_id=transaction_id,
            action=action,
            recovery_probability=probability,
            expected_recovery_value=erv,
            policy_decision=policy_decision,
            execution_status=execution_status,
            verification_status=verification_status,
            final_status=final_status,
            amount_recovered=amount_recovered,
            timestamp=datetime.utcnow()
        )

        db.add(log)
        db.commit()
        db.refresh(log)

        return {
            "id": log.id,
            "transaction_id": log.transaction_id,
            "timestamp": log.timestamp.isoformat(),
            "action": log.action,
            "recovery_probability": log.recovery_probability,
            "expected_recovery_value": log.expected_recovery_value,
            "policy_decision": log.policy_decision,
            "execution_status": log.execution_status,
            "verification_status": log.verification_status,
            "final_status": log.final_status,
            "amount_recovered": log.amount_recovered
        }

    finally:

        db.close()


# ============================================================
# MAIN RECOVERY AGENT
# ============================================================

def run_recovery_agent(transaction_id):

    state_history = [
        "DETECTED"
    ]

    # ========================================================
    # STEP 1 — GET TRANSACTION
    # ========================================================

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
                "message": "Transaction not found.",
                "state_history": state_history
            }

        amount = float(transaction.amount)
        payment_method = transaction.payment_method
        failure_reason = transaction.failure_reason

        # ----------------------------------------------------
        # Already recovered protection
        # ----------------------------------------------------

        if transaction.status == "SUCCESS":

            state_history.extend([
                "INVESTIGATING",
                "EVALUATING",
                "POLICY_CHECK",
                "RECOVERED"
            ])

            return {
                "transaction_id": transaction_id,
                "customer": (
                    db.query(Customer)
                    .filter(
                        Customer.customer_id ==
                        transaction.customer_id
                    )
                    .first().name
                    if db.query(Customer)
                    .filter(
                        Customer.customer_id ==
                        transaction.customer_id
                    )
                    .first()
                    else None
                ),
                "status": "ALREADY_RECOVERED",
                "message": (
                    "Recovery stopped because this transaction "
                    "was already successful."
                ),
                "final_status": "RECOVERED",
                "amount_recovered": amount,
                "state_history": state_history
            }

        retry_count = transaction.retry_count or 0

        customer = (
            db.query(Customer)
            .filter(
                Customer.customer_id ==
                transaction.customer_id
            )
            .first()
        )

        customer_name = (
            customer.name if customer else None
        )

    finally:

        db.close()

    # ========================================================
    # STEP 2 — INVESTIGATE
    # ========================================================

    state_history.append("INVESTIGATING")

    investigation = investigate_payment(
        transaction_id
    )

    if "error" in investigation:

        return {
            "transaction_id": transaction_id,
            "final_status": "ERROR",
            "message": investigation["error"],
            "state_history": state_history
        }

    recovery_probability = investigation[
        "recovery_probability"
    ]

    # ========================================================
    # STEP 3 — EXPECTED RECOVERY VALUE
    # ========================================================

    state_history.append("EVALUATING")

    erv = calculate_expected_recovery_value(
        amount,
        recovery_probability
    )

    expected_recovery_value = erv[
        "expected_recovery_value"
    ]

    # ========================================================
    # STEP 4 — CHOOSE INTERVENTION
    # ========================================================

    intervention = choose_intervention(
        failure_reason=failure_reason,
        recovery_probability=recovery_probability,
        expected_recovery_value=expected_recovery_value,
        amount=amount
    )

    action = intervention["action"]

    # ========================================================
    # STEP 5 — POLICY CHECK
    # ========================================================

    state_history.append("POLICY_CHECK")

    policy = check_policy(
        transaction_id=transaction_id,
        action=action,
        amount=amount,
        retry_count=retry_count
    )

    # --------------------------------------------------------
    # POLICY BLOCK / ESCALATION
    # --------------------------------------------------------

    if policy["decision"] == "ESCALATE":

        state_history.append("ESCALATED")

        return {
            "transaction_id": transaction_id,
            "customer": customer_name,
            "amount": amount,
            "recovery_probability": recovery_probability,
            "expected_recovery_value": expected_recovery_value,
            "intervention": intervention,
            "policy": policy,
            "final_status": "ESCALATE",
            "amount_recovered": 0,
            "message": policy["reason"],
            "state_history": state_history
        }

    if policy["decision"] == "STOP":

        state_history.append("STOPPED")

        return {
            "transaction_id": transaction_id,
            "customer": customer_name,
            "amount": amount,
            "recovery_probability": recovery_probability,
            "expected_recovery_value": expected_recovery_value,
            "intervention": intervention,
            "policy": policy,
            "final_status": "STOPPED",
            "amount_recovered": 0,
            "message": policy["reason"],
            "state_history": state_history
        }

    if policy["decision"] == "RECOVERED":

        state_history.append("RECOVERED")

        return {
            "transaction_id": transaction_id,
            "customer": customer_name,
            "status": "ALREADY_RECOVERED",
            "message": policy["reason"],
            "final_status": "RECOVERED",
            "amount_recovered": amount,
            "state_history": state_history
        }

    # ========================================================
    # STEP 6 — TRACK RECOVERY ATTEMPT
    # ========================================================

    tracking = record_recovery_attempt(
        transaction_id,
        action
    )

    # ========================================================
    # STEP 7 — EXECUTE
    # ========================================================

    state_history.append("EXECUTING")

    execution = execute_action(
        action=action,
        transaction_id=transaction_id,
        amount=amount,
        payment_method=payment_method
    )

    # ========================================================
    # STEP 8 — VERIFY
    # ========================================================

    state_history.append("VERIFYING")

    verification = verify_recovery(
        transaction_id=transaction_id,
        action=action,
        failure_reason=failure_reason,
        payment_attempted=execution[
            "payment_attempted"
        ]
    )

    # ========================================================
    # STEP 9 — DETERMINE FINAL STATUS
    # ========================================================

    if verification["status"] == "RECOVERED":

        final_status = "RECOVERED"
        amount_recovered = amount
        state_history.append("RECOVERED")

    else:

        final_status = "RECOVERY_FAILED"
        amount_recovered = 0
        state_history.append("RECOVERY_FAILED")

    # ========================================================
    # STEP 10 — LOG DECISION
    # ========================================================

    log_recovery_decision(
        transaction_id=transaction_id,
        action=action,
        probability=recovery_probability,
        erv=expected_recovery_value,
        policy_decision=policy["decision"],
        execution_status=execution["status"],
        verification_status=verification["status"],
        final_status=final_status,
        amount_recovered=amount_recovered
    )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {
        "transaction_id": transaction_id,
        "customer": customer_name,
        "amount": amount,
        "recovery_probability": recovery_probability,
        "expected_recovery_value": expected_recovery_value,

        "erv": erv,

        "intervention": intervention,

        "policy": policy,

        "tracking": tracking,

        "execution": execution,

        "verification": verification,

        "final_status": final_status,

        "amount_recovered": amount_recovered,

        "state_history": state_history
    }