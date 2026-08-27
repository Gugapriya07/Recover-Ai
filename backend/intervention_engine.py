def choose_intervention(
    failure_reason,
    recovery_probability,
    expected_recovery_value,
    amount
):
    """
    Decide the best bounded recovery intervention.

    Decision is based on:
        1. Recovery probability
        2. Expected recovery value
        3. Failure reason
        4. Transaction amount

    recovery_probability:
        Percentage from 0 to 100.

    expected_recovery_value:
        Expected monetary value in INR.
    """

    # =========================================================
    # NORMALIZE INPUTS
    # =========================================================

    failure_reason = str(
        failure_reason
    ).upper()

    recovery_probability = float(
        recovery_probability
    )

    expected_recovery_value = float(
        expected_recovery_value
    )

    amount = float(
        amount
    )


    # =========================================================
    # 1. VERY LOW RECOVERY PROBABILITY
    # =========================================================

    if recovery_probability < 20:

        return {
            "action": "STOP",
            "priority": "LOW",
            "reason": (
                "Recovery probability is too low "
                "to justify an autonomous recovery attempt."
            )
        }


    # =========================================================
    # 2. VERY LOW EXPECTED RECOVERY VALUE
    # =========================================================

    if expected_recovery_value < 100:

        return {
            "action": "STOP",
            "priority": "LOW",
            "reason": (
                "Expected recovery value is too low "
                "to justify further recovery effort."
            )
        }


    # =========================================================
    # 3. INSUFFICIENT FUNDS
    # =========================================================

    if failure_reason == "INSUFFICIENT_FUNDS":

        if recovery_probability >= 70:

            return {
                "action": "WAIT_AND_RETRY",
                "priority": "HIGH",
                "reason": (
                    "High recovery probability for insufficient funds. "
                    "Waiting before retry may give the customer time "
                    "to replenish funds."
                )
            }

        return {
            "action": "SEND_PAYMENT_REMINDER",
            "priority": "MEDIUM",
            "reason": (
                "Customer may need to replenish funds before "
                "another payment attempt."
            )
        }


    # =========================================================
    # 4. UPI TIMEOUT
    # =========================================================

    if failure_reason == "UPI_TIMEOUT":

        if recovery_probability >= 60:

            return {
                "action": "RETRY_PAYMENT",
                "priority": "HIGH",
                "reason": (
                    "UPI failure appears temporary and has a "
                    "good recovery probability, so a retry is justified."
                )
            }

        return {
            "action": "WAIT_AND_RETRY",
            "priority": "MEDIUM",
            "reason": (
                "UPI failure may be temporary, so waiting before "
                "another attempt is safer."
            )
        }


    # =========================================================
    # 5. CARD EXPIRED
    # =========================================================

    if failure_reason == "CARD_EXPIRED":

        return {
            "action": "REQUEST_NEW_PAYMENT_METHOD",
            "priority": "HIGH",
            "reason": (
                "The current card is expired and should not be "
                "retried. A new payment method is required."
            )
        }


    # =========================================================
    # 6. AUTHENTICATION FAILED
    # =========================================================

    if failure_reason == "AUTHENTICATION_FAILED":

        if recovery_probability >= 60:

            return {
                "action": "REQUEST_REAUTHENTICATION",
                "priority": "HIGH",
                "reason": (
                    "Authentication failure has reasonable recovery "
                    "potential, so customer reauthentication is appropriate."
                )
            }

        return {
            "action": "REQUEST_NEW_PAYMENT_METHOD",
            "priority": "MEDIUM",
            "reason": (
                "Authentication recovery confidence is limited, "
                "so requesting another payment method is safer."
            )
        }


    # =========================================================
    # 7. BANK DECLINED
    # =========================================================

    if failure_reason == "BANK_DECLINED":

        # High confidence:
        # directly try another payment method.
        if recovery_probability >= 60:

            return {
                "action": "TRY_ALTERNATIVE_PAYMENT",
                "priority": "HIGH",
                "reason": (
                    "The bank declined the original payment. "
                    "Recovery probability is high enough to justify "
                    "trying an alternative payment method."
                )
            }

        # Medium confidence:
        # alternative payment can still be economically justified.
        if recovery_probability >= 30:

            return {
                "action": "TRY_ALTERNATIVE_PAYMENT",
                "priority": "MEDIUM",
                "reason": (
                    "The bank declined the original payment, but the "
                    "expected recovery value justifies a bounded "
                    "alternative payment attempt."
                )
            }

        # Below 30%, stop autonomous recovery.
        return {
            "action": "ESCALATE",
            "priority": "HIGH",
            "reason": (
                "Bank decline has low recovery confidence and "
                "does not justify further autonomous payment attempts."
            )
        }


    # =========================================================
    # 8. PAYMENT FAILED
    # =========================================================

    if failure_reason == "PAYMENT_FAILED":

        if recovery_probability >= 60:

            return {
                "action": "RETRY_PAYMENT",
                "priority": "HIGH",
                "reason": (
                    "The payment failure has a good recovery probability, "
                    "so a bounded retry is justified."
                )
            }

        if recovery_probability >= 30:

            return {
                "action": "WAIT_AND_RETRY",
                "priority": "MEDIUM",
                "reason": (
                    "Recovery probability is moderate, so waiting before "
                    "another attempt reduces unnecessary repeated retries."
                )
            }

        return {
            "action": "ESCALATE",
            "priority": "MEDIUM",
            "reason": (
                "Recovery probability is too low for autonomous retry."
            )
        }


    # =========================================================
    # 9. UNKNOWN FAILURE
    # =========================================================

    return {
        "action": "ESCALATE",
        "priority": "MEDIUM",
        "reason": (
            "Unknown payment failure requires further investigation "
            "before autonomous recovery."
        )
    }