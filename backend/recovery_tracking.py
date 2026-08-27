from database import SessionLocal
from models import Transaction


# ============================================================
# RECOVERY SAFETY CONFIGURATION
# ============================================================

MAX_RETRIES = 3


# Actions that actually attempt a payment.
# These actions consume one retry attempt.
RETRY_ACTIONS = {
    "RETRY_PAYMENT",
    "WAIT_AND_RETRY",
    "TRY_ALTERNATIVE_PAYMENT"
}


# Terminal states where no further autonomous recovery
# should be attempted.
TERMINAL_STATES = {
    "RECOVERED",
    "SUCCESS",
    "PAYMENT_PENDING",
    "STOPPED"
}


# ============================================================
# CHECK WHETHER RECOVERY IS ALLOWED
# ============================================================

def can_attempt_recovery(transaction_id, action=None):
    """
    Determine whether RecoverAI is allowed to perform
    another recovery attempt.

    Safety rules:

    1. Transaction must exist.
    2. Successful/recovered transactions cannot be recovered again.
    3. Pending transactions cannot be recovered again.
    4. Stopped transactions cannot be recovered again.
    5. Payment retry actions are limited to MAX_RETRIES.
    6. Recovery-failed transactions may retry until the limit.
    """

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # FIND TRANSACTION
        # ----------------------------------------------------

        transaction = db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()

        if not transaction:

            return {
                "allowed": False,
                "reason": "Transaction not found.",
                "retry_count": 0
            }


        # ----------------------------------------------------
        # CURRENT RETRY COUNT
        # ----------------------------------------------------

        retry_count = transaction.retry_count or 0


        # ----------------------------------------------------
        # CHECK TERMINAL TRANSACTION STATES
        # ----------------------------------------------------

        current_status = (
            getattr(transaction, "status", None)
            or ""
        ).upper()

        final_status = (
            getattr(transaction, "final_status", None)
            or ""
        ).upper()


        # SUCCESS / RECOVERED
        if (
            current_status in {"SUCCESS", "RECOVERED"}
            or final_status in {"SUCCESS", "RECOVERED"}
        ):

            return {
                "allowed": False,
                "reason": (
                    "Recovery blocked because the transaction "
                    "has already been successfully recovered."
                ),
                "retry_count": retry_count
            }


        # PAYMENT PENDING
        if (
            current_status == "PAYMENT_PENDING"
            or final_status == "PAYMENT_PENDING"
        ):

            return {
                "allowed": False,
                "reason": (
                    "Recovery blocked because payment "
                    "is already pending."
                ),
                "retry_count": retry_count
            }


        # STOPPED
        if (
            current_status == "STOPPED"
            or final_status == "STOPPED"
        ):

            return {
                "allowed": False,
                "reason": (
                    "Recovery blocked because the transaction "
                    "has already been stopped."
                ),
                "retry_count": retry_count
            }


        # ----------------------------------------------------
        # CHECK RETRY LIMIT
        # ----------------------------------------------------

        if action in RETRY_ACTIONS:

            if retry_count >= MAX_RETRIES:

                return {
                    "allowed": False,
                    "reason": (
                        f"Maximum retry limit of {MAX_RETRIES} "
                        "has been reached."
                    ),
                    "retry_count": retry_count,
                    "max_retries": MAX_RETRIES
                }


        # ----------------------------------------------------
        # RECOVERY ALLOWED
        # ----------------------------------------------------

        return {
            "allowed": True,
            "reason": "Recovery attempt is allowed.",
            "retry_count": retry_count,
            "max_retries": MAX_RETRIES
        }


    finally:

        db.close()


# ============================================================
# RECORD RECOVERY ATTEMPT
# ============================================================

def record_recovery_attempt(transaction_id, action):
    """
    Record a recovery attempt.

    Only actual payment-attempt actions increase retry_count.

    Example:

        RETRY_PAYMENT
            retry_count += 1

        TRY_ALTERNATIVE_PAYMENT
            retry_count += 1

        SEND_PAYMENT_REMINDER
            retry_count unchanged

        REQUEST_NEW_PAYMENT_METHOD
            retry_count unchanged
    """

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # FIND TRANSACTION
        # ----------------------------------------------------

        transaction = db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()

        if not transaction:

            return {
                "recorded": False,
                "reason": "Transaction not found."
            }


        # ----------------------------------------------------
        # CURRENT RETRY COUNT
        # ----------------------------------------------------

        retry_count = transaction.retry_count or 0


        # ----------------------------------------------------
        # INCREMENT ONLY FOR PAYMENT ATTEMPTS
        # ----------------------------------------------------

        if action in RETRY_ACTIONS:

            # Safety check:
            # never allow retry_count to exceed MAX_RETRIES.

            if retry_count >= MAX_RETRIES:

                return {
                    "recorded": False,
                    "reason": (
                        f"Maximum retry limit of {MAX_RETRIES} "
                        "has already been reached."
                    ),
                    "transaction_id": transaction_id,
                    "action": action,
                    "retry_count": retry_count,
                    "max_retries": MAX_RETRIES
                }


            transaction.retry_count = retry_count + 1


        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        db.commit()

        db.refresh(transaction)


        # ----------------------------------------------------
        # RETURN RESULT
        # ----------------------------------------------------

        return {
            "recorded": True,
            "transaction_id": transaction_id,
            "action": action,
            "retry_count": transaction.retry_count or 0,
            "max_retries": MAX_RETRIES
        }


    finally:

        db.close()