# =========================================================
# POLICY ENGINE
# RecoverAI
# =========================================================


def check_policy(
    action,
    amount,
    recovery_probability,
    expected_recovery_value,
    retry_count,
    payment_status,
    failure_reason
):
    """
    Validate an AI recovery decision against
    RecoverAI safety and recovery policies.
    """

    # =====================================================
    # NORMALIZE INPUTS
    # =====================================================

    action = str(action or "").upper()
    payment_status = str(payment_status or "").upper()
    failure_reason = str(failure_reason or "").upper()

    amount = float(amount or 0)
    recovery_probability = float(
        recovery_probability or 0
    )
    expected_recovery_value = float(
        expected_recovery_value or 0
    )
    retry_count = int(retry_count or 0)

    MAX_RETRIES = 3
    MIN_PROBABILITY = 20
    MIN_ERV = 100
    MAX_AUTONOMOUS_AMOUNT = 10000

    retry_actions = {
        "RETRY_PAYMENT",
        "WAIT_AND_RETRY",
        "TRY_ALTERNATIVE_PAYMENT"
    }

    # =====================================================
    # POLICY 1
    # ALREADY SUCCESSFUL
    # =====================================================

    if payment_status in {
        "SUCCESS",
        "RECOVERED"
    }:

        return {
            "approved": False,
            "decision": "BLOCK",
            "reason": (
                "Payment is already successful. "
                "No further recovery action is allowed."
            )
        }

    # =====================================================
    # POLICY 2
    # STOP IS AN INTENTIONAL TERMINAL DECISION
    #
    # IMPORTANT:
    # Check STOP before probability/ERV rules.
    # =====================================================

    if action == "STOP":

        return {
            "approved": True,
            "decision": "STOP",
            "reason": (
                "AI determined that autonomous recovery "
                "is not justified."
            )
        }

    # =====================================================
    # POLICY 3
    # ESCALATE IS AN INTENTIONAL TERMINAL DECISION
    # =====================================================

    if action == "ESCALATE":

        return {
            "approved": True,
            "decision": "ESCALATE",
            "reason": (
                "Recovery requires manual intervention."
            )
        }

    # =====================================================
    # POLICY 4
    # MAXIMUM RETRY LIMIT
    # =====================================================

    if action in retry_actions:

        if retry_count >= MAX_RETRIES:

            return {
                "approved": False,
                "decision": "STOP",
                "reason": (
                    f"Maximum retry limit of {MAX_RETRIES} "
                    "has been reached."
                )
            }

    # =====================================================
    # POLICY 5
    # MINIMUM RECOVERY PROBABILITY
    # =====================================================

    if recovery_probability < MIN_PROBABILITY:

        return {
            "approved": False,
            "decision": "STOP",
            "reason": (
                "Recovery probability is below the allowed "
                "threshold. Further autonomous recovery "
                "attempts are stopped."
            )
        }

    # =====================================================
    # POLICY 6
    # MINIMUM EXPECTED RECOVERY VALUE
    # =====================================================

    if expected_recovery_value < MIN_ERV:

        return {
            "approved": False,
            "decision": "STOP",
            "reason": (
                "Expected recovery value is too low "
                "to justify autonomous recovery."
            )
        }

    # =====================================================
    # POLICY 7
    # MAXIMUM AUTONOMOUS TRANSACTION AMOUNT
    # =====================================================

    if amount > MAX_AUTONOMOUS_AMOUNT:

        return {
            "approved": False,
            "decision": "ESCALATE",
            "reason": (
                "Transaction amount exceeds the autonomous "
                "recovery limit. Manual review is required."
            )
        }

    # =====================================================
    # POLICY 8
    # EXPIRED CARD PROTECTION
    # =====================================================

    if failure_reason == "CARD_EXPIRED":

        if action in retry_actions:

            return {
                "approved": False,
                "decision": "BLOCK",
                "reason": (
                    "Expired cards cannot be retried. "
                    "A new payment method is required."
                )
            }

    # =====================================================
    # POLICY 9
    # AUTHENTICATION FAILURE
    # =====================================================

    if failure_reason == "AUTHENTICATION_FAILED":

        if recovery_probability < 40:

            return {
                "approved": False,
                "decision": "STOP",
                "reason": (
                    "Authentication failure has low recovery "
                    "probability. Recovery process stopped."
                )
            }

    # =====================================================
    # POLICY 10
    # BANK DECLINED
    # =====================================================

    if failure_reason == "BANK_DECLINED":

        if recovery_probability < 30:

            return {
                "approved": False,
                "decision": "ESCALATE",
                "reason": (
                    "Bank-declined payment has low recovery "
                    "probability. Manual review is required."
                )
            }

    # =====================================================
    # POLICY 11
    # ALL POLICIES PASSED
    # =====================================================

    return {
        "approved": True,
        "decision": "APPROVE",
        "reason": "All recovery policies passed."
    }