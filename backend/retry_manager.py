from database import SessionLocal
from models import RecoveryLog


# =========================================================
# CONFIGURATION
# =========================================================

MAX_RECOVERY_ATTEMPTS = 3


# =========================================================
# GET RETRY COUNT
# =========================================================

def get_retry_count(transaction_id: str):

    db = SessionLocal()

    try:

        count = (
            db.query(RecoveryLog)
            .filter(
                RecoveryLog.transaction_id == transaction_id
            )
            .count()
        )

        return count

    finally:

        db.close()


# =========================================================
# CHECK WHETHER RECOVERY CAN BE ATTEMPTED
# =========================================================

def can_attempt_recovery(transaction_id: str):

    retry_count = get_retry_count(
        transaction_id
    )

    return retry_count < MAX_RECOVERY_ATTEMPTS


# =========================================================
# RECORD RECOVERY ATTEMPT
# =========================================================

def record_recovery_attempt(
    transaction,
    action: str,
    status: str
):

    retry_count = get_retry_count(
        transaction.transaction_id
    )

    current_attempt = retry_count + 1

    remaining_attempts = max(
        0,
        MAX_RECOVERY_ATTEMPTS - current_attempt
    )

    return {

        "transaction_id":
            transaction.transaction_id,

        "action":
            action,

        "status":
            status,

        "retry_count":
            current_attempt,

        "recovery_attempts":
            current_attempt,

        "max_attempts":
            MAX_RECOVERY_ATTEMPTS,

        "remaining_attempts":
            remaining_attempts

    }