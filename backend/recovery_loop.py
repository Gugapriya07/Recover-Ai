from action_executor import execute_action
from verification import verify_payment


# =========================================================
# RUN ONE RECOVERY ATTEMPT
# =========================================================

def run_recovery_attempt(
    transaction_id,
    action,
    amount,
    payment_method,
    recovery_probability
):
    """
    Execute one bounded recovery attempt.

    Flow:

        Execute
           ↓
        Verify
           ↓
        Final Status
    """

    # =====================================================
    # 1. EXECUTE
    # =====================================================

    execution = execute_action(
        action=action,
        transaction_id=transaction_id,
        amount=amount,
        payment_method=payment_method,
        recovery_probability=recovery_probability
    )

    execution_status = str(
        execution.get(
            "status",
            "REJECTED"
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

    # =====================================================
    # 2. EXECUTION REJECTED / STOPPED
    # =====================================================

    if execution_status in [
        "REJECTED",
        "STOPPED"
    ]:

        return {
            "transaction_id":
                transaction_id,

            "execution":
                execution,

            "verification":
                None,

            "final_status":
                "STOPPED",

            "amount_recovered":
                0
        }

    # =====================================================
    # 3. ACTUAL PAYMENT RECOVERED
    # =====================================================

    if payment_recovered:

        verification = {
            "transaction_id":
                transaction_id,

            "action":
                action,

            "status":
                "RECOVERED",

            "payment_successful":
                True,

            "message":
                "Payment recovery verified successfully."
        }

        return {
            "transaction_id":
                transaction_id,

            "execution":
                execution,

            "verification":
                verification,

            "final_status":
                "RECOVERED",

            "amount_recovered":
                float(amount)
        }

    # =====================================================
    # 4. NON-PAYMENT INTERVENTION
    # =====================================================

    if (
        execution_status in [
            "EXECUTED",
            "SCHEDULED"
        ]
        and not payment_attempted
    ):

        verification = {
            "transaction_id":
                transaction_id,

            "action":
                action,

            "status":
                "PAYMENT_PENDING",

            "payment_successful":
                False,

            "message":
                (
                    "Recovery intervention executed "
                    "successfully. Payment is awaiting "
                    "customer action."
                )
        }

        return {
            "transaction_id":
                transaction_id,

            "execution":
                execution,

            "verification":
                verification,

            "final_status":
                "PAYMENT_PENDING",

            "amount_recovered":
                0
        }

    # =====================================================
    # 5. PAYMENT ATTEMPTED BUT FAILED
    # =====================================================

    if payment_attempted and not payment_recovered:

        verification = {
            "transaction_id":
                transaction_id,

            "action":
                action,

            "status":
                "RECOVERY_FAILED",

            "payment_successful":
                False,

            "message":
                "Payment recovery could not be verified."
        }

        return {
            "transaction_id":
                transaction_id,

            "execution":
                execution,

            "verification":
                verification,

            "final_status":
                "RECOVERY_FAILED",

            "amount_recovered":
                0
        }

    # =====================================================
    # 6. UNKNOWN RESULT
    # =====================================================

    verification = {
        "transaction_id":
            transaction_id,

        "action":
            action,

        "status":
            "RECOVERY_FAILED",

        "payment_successful":
            False,

        "message":
            "Payment recovery could not be verified."
    }

    return {
        "transaction_id":
            transaction_id,

        "execution":
            execution,

        "verification":
            verification,

        "final_status":
            "RECOVERY_FAILED",

        "amount_recovered":
            0
    }