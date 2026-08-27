from database import SessionLocal
from models import RecoveryLog, Transaction


# =========================================================
# SAVE RECOVERY LOG
# =========================================================

def save_recovery_log(
    transaction_id,
    action,
    recovery_probability,
    expected_recovery_value,
    policy_decision,
    execution_status,
    verification_status,
    final_status,
    amount_recovered
):
    """
    Save the complete recovery decision and execution trail.
    """

    db = SessionLocal()

    try:

        log = RecoveryLog(
            transaction_id=transaction_id,
            action=action,
            recovery_probability=recovery_probability,
            expected_recovery_value=expected_recovery_value,
            policy_decision=policy_decision,
            execution_status=execution_status,
            verification_status=verification_status,
            final_status=final_status,
            amount_recovered=amount_recovered
        )

        db.add(log)
        db.commit()
        db.refresh(log)

        return log

    finally:
        db.close()


# =========================================================
# GET RECOVERY HISTORY
# =========================================================

def get_recovery_history(transaction_id):
    """
    Return recovery history for one transaction.

    Latest recovery attempt comes first.
    """

    db = SessionLocal()

    try:

        logs = (
            db.query(RecoveryLog)
            .filter(
                RecoveryLog.transaction_id ==
                transaction_id
            )
            .order_by(
                RecoveryLog.id.desc()
            )
            .all()
        )

        history = []

        for log in logs:

            history.append({

                "id":
                    log.id,

                "transaction_id":
                    log.transaction_id,

                "timestamp":
                    str(log.timestamp),

                "action":
                    log.action,

                "recovery_probability":
                    float(
                        log.recovery_probability or 0
                    ),

                "expected_recovery_value":
                    float(
                        log.expected_recovery_value or 0
                    ),

                "policy_decision":
                    log.policy_decision,

                "execution_status":
                    log.execution_status,

                "verification_status":
                    log.verification_status,

                "final_status":
                    log.final_status,

                "amount_recovered":
                    float(
                        log.amount_recovered or 0
                    )
            })

        return history

    finally:

        db.close()

# =========================================================
# GET ALL RECOVERY LOGS
# =========================================================

def get_recovery_logs():
    """
    Return all recovery logs with the original
    transaction amount.

    Latest logs come first.
    """

    db = SessionLocal()

    try:

        logs = (
            db.query(RecoveryLog)
            .order_by(
                RecoveryLog.id.desc()
            )
            .all()
        )

        result = []

        for log in logs:

            # -------------------------------------------------
            # GET ORIGINAL TRANSACTION
            # -------------------------------------------------

            transaction = (
                db.query(Transaction)
                .filter(
                    Transaction.transaction_id
                    == log.transaction_id
                )
                .first()
            )

            transaction_amount = (
                float(transaction.amount or 0)
                if transaction
                else 0.0
            )

            result.append({

                "id":
                    log.id,

                "transaction_id":
                    log.transaction_id,

                "timestamp":
                    str(log.timestamp),

                "amount":
                    transaction_amount,

                "action":
                    log.action,

                "recovery_probability":
                    float(
                        log.recovery_probability or 0
                    ),

                "expected_recovery_value":
                    float(
                        log.expected_recovery_value or 0
                    ),

                "policy_decision":
                    log.policy_decision,

                "execution_status":
                    log.execution_status,

                "verification_status":
                    log.verification_status,

                "final_status":
                    log.final_status,

                "amount_recovered":
                    float(
                        log.amount_recovered or 0
                    )
            })

        return result

    finally:

        db.close()