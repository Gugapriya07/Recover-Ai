from datetime import datetime


def verify_payment(
    transaction_id,
    action,
    recovery_probability,
    execution=None
):
    """
    Verify the result of a recovery action.

    The execution layer determines whether the simulated
    payment was actually recovered.

    This layer confirms that result.
    """

    timestamp = datetime.utcnow().isoformat()

    execution = execution or {}

    # =========================================================
    # ACTIONS THAT DO NOT DIRECTLY COMPLETE PAYMENT
    # =========================================================

    if action in [
        "STOP",
        "ESCALATE",
        "SEND_PAYMENT_REMINDER",
        "WAIT_AND_RETRY",
        "REQUEST_NEW_PAYMENT_METHOD",
        "REQUEST_REAUTHENTICATION"
    ]:

        return {
            "transaction_id": transaction_id,
            "action": action,
            "status": "PAYMENT_PENDING",
            "payment_successful": False,
            "message": (
                "Recovery action was executed, "
                "but payment has not yet been completed."
            ),
            "timestamp": timestamp
        }


    # =========================================================
    # PAYMENT ATTEMPT WAS NOT EXECUTED
    # =========================================================

    if not execution.get(
        "payment_attempted",
        False
    ):

        return {
            "transaction_id": transaction_id,
            "action": action,
            "status": "PAYMENT_PENDING",
            "payment_successful": False,
            "message": (
                "No payment attempt was performed."
            ),
            "timestamp": timestamp
        }


    # =========================================================
    # VERIFY PAYMENT RESULT
    # =========================================================

    payment_recovered = execution.get(
        "payment_recovered",
        False
    )


    # =========================================================
    # RECOVERED
    # =========================================================

    if payment_recovered:

        return {
            "transaction_id": transaction_id,
            "action": action,
            "status": "RECOVERED",
            "payment_successful": True,
            "message": (
                "Payment gateway verification confirmed "
                "successful recovery."
            ),
            "recovery_probability": recovery_probability,
            "timestamp": timestamp
        }


    # =========================================================
    # FAILED
    # =========================================================

    return {
        "transaction_id": transaction_id,
        "action": action,
        "status": "FAILED",
        "payment_successful": False,
        "message": (
            "Payment gateway verification did not "
            "confirm successful recovery."
        ),
        "recovery_probability": recovery_probability,
        "timestamp": timestamp
    }