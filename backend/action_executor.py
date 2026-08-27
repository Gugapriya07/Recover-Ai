from database import SessionLocal
from models import Transaction


def execute_action(
    action,
    transaction_id,
    amount,
    payment_method
):
    """
    Execute a bounded recovery action.

    This is a simulation layer for RecoverAI.
    It does NOT perform a real payment.
    """

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
                "status": "FAILED",
                "execution_status": "FAILED",
                "payment_attempted": False,
                "payment_recovered": False,
                "message": "Transaction not found."
            }

        # -------------------------------------------------
        # SAFETY: NEVER EXECUTE ON SUCCESS
        # -------------------------------------------------

        if str(transaction.status).upper() in [
            "SUCCESS",
            "RECOVERED"
        ]:

            return {
                "status": "BLOCKED",
                "execution_status": "BLOCKED",
                "payment_attempted": False,
                "payment_recovered": False,
                "message": (
                    "Payment is already successful. "
                    "Recovery action blocked."
                )
            }

        # -------------------------------------------------
        # STOP
        # -------------------------------------------------

        if action == "STOP":

            return {
                "status": "STOPPED",
                "execution_status": "NOT_EXECUTED",
                "payment_attempted": False,
                "payment_recovered": False,
                "message": "Recovery action stopped."
            }

        # -------------------------------------------------
        # ESCALATE
        # -------------------------------------------------

        if action == "ESCALATE":

            return {
                "status": "ESCALATED",
                "execution_status": "NOT_EXECUTED",
                "payment_attempted": False,
                "payment_recovered": False,
                "message": (
                    "Recovery escalated for manual intervention."
                )
            }

        # -------------------------------------------------
        # PAYMENT RETRY
        # -------------------------------------------------

        if action in [
            "RETRY_PAYMENT",
            "WAIT_AND_RETRY"
        ]:

            # -------------------------------------------------
            # SIMULATION
            #
            # Change these transaction IDs when you want
            # different demo outcomes.
            # -------------------------------------------------

            recovery_transactions = {
                "TXN_1010",
                "TXN_1017",
                "TXN_1024"
            }

            if transaction_id in recovery_transactions:

                transaction.status = "RECOVERED"

                db.commit()

                return {
                    "status": "RECOVERED",
                    "execution_status": "RECOVERED",
                    "payment_attempted": True,
                    "payment_recovered": True,
                    "amount_recovered": float(amount),
                    "message": (
                        "Payment retry successfully recovered "
                        "the transaction."
                    )
                }

            return {
                "status": "RECOVERY_FAILED",
                "execution_status": "RECOVERY_FAILED",
                "payment_attempted": True,
                "payment_recovered": False,
                "amount_recovered": 0,
                "message": (
                    "Payment retry was executed but "
                    "payment was not recovered."
                )
            }

        # -------------------------------------------------
        # ALTERNATIVE PAYMENT
        # -------------------------------------------------

        if action == "TRY_ALTERNATIVE_PAYMENT":

            recovery_transactions = {
                "TXN_1007"
            }

            if transaction_id in recovery_transactions:

                transaction.status = "RECOVERED"

                db.commit()

                return {
                    "status": "RECOVERED",
                    "execution_status": "RECOVERED",
                    "payment_attempted": True,
                    "payment_recovered": True,
                    "amount_recovered": float(amount),
                    "message": (
                        "Alternative payment method "
                        "successfully recovered the payment."
                    )
                }

            return {
                "status": "RECOVERY_FAILED",
                "execution_status": "RECOVERY_FAILED",
                "payment_attempted": True,
                "payment_recovered": False,
                "amount_recovered": 0,
                "message": (
                    "Alternative payment attempt failed."
                )
            }

        # -------------------------------------------------
        # NON-PAYMENT INTERVENTIONS
        # -------------------------------------------------

        if action in [
            "SEND_PAYMENT_REMINDER",
            "SEND_RECOVERY_MESSAGE",
            "SEND_PAYMENT_LINK",
            "REQUEST_NEW_PAYMENT_METHOD"
        ]:

            transaction.status = "PAYMENT_PENDING"

            db.commit()

            return {
                "status": "PAYMENT_PENDING",
                "execution_status": "EXECUTED",
                "payment_attempted": False,
                "payment_recovered": False,
                "amount_recovered": 0,
                "message": (
                    f"{action} executed successfully. "
                    "Waiting for customer action."
                )
            }

        # -------------------------------------------------
        # UNKNOWN ACTION
        # -------------------------------------------------

        return {
            "status": "FAILED",
            "execution_status": "FAILED",
            "payment_attempted": False,
            "payment_recovered": False,
            "amount_recovered": 0,
            "message": (
                f"Unknown recovery action: {action}"
            )
        }

    finally:

        db.close()