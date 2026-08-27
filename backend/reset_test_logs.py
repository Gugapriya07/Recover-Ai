from database import SessionLocal
from models import RecoveryLog

TRANSACTIONS_TO_RESET = [
    "TXN_1001",
    "TXN_1004",
]

db = SessionLocal()

try:
    deleted = (
        db.query(RecoveryLog)
        .filter(
            RecoveryLog.transaction_id.in_(
                TRANSACTIONS_TO_RESET
            )
        )
        .delete(
            synchronize_session=False
        )
    )

    db.commit()

    print(
        f"Deleted {deleted} recovery log(s)."
    )

    for transaction_id in TRANSACTIONS_TO_RESET:

        remaining = (
            db.query(RecoveryLog)
            .filter(
                RecoveryLog.transaction_id ==
                transaction_id
            )
            .count()
        )

        print(
            f"{transaction_id}: "
            f"{remaining} recovery logs remaining"
        )

finally:

    db.close()