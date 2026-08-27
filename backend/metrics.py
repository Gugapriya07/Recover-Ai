from database import SessionLocal
from models import Transaction


def get_recovery_metrics():
    """
    Calculate revenue recovery metrics across all transactions.
    """

    db = SessionLocal()

    try:
        transactions = db.query(Transaction).all()

        total_transactions = len(transactions)

        total_revenue_at_risk = 0.0
        expected_recovery_value = 0.0
        total_amount_recovered = 0.0

        pending_amount = 0.0
        escalated_amount = 0.0
        stopped_amount = 0.0
        failed_amount = 0.0

        recovered_transactions = 0
        pending_transactions = 0
        escalated_transactions = 0
        stopped_transactions = 0
        failed_transactions = 0

        successful_transactions = 0

        for transaction in transactions:

            amount = float(
                transaction.amount or 0
            )

            status = str(
                transaction.status or ""
            ).upper()

            # -------------------------------------------------
            # SUCCESSFUL / RECOVERED
            # -------------------------------------------------

            if status in {"SUCCESS", "RECOVERED"}:

                successful_transactions += 1

                recovered_transactions += 1

                total_amount_recovered += amount

                continue

            # -------------------------------------------------
            # FAILED / AT RISK
            # -------------------------------------------------

            total_revenue_at_risk += amount

            failed_amount += amount

            failed_transactions += 1

        # -----------------------------------------------------
        # RECOVERY LOGS
        # -----------------------------------------------------

        from recovery_log import get_recovery_logs

        logs = get_recovery_logs()

        # Use recovery logs to calculate expected recovery
        # and terminal workflow amounts.

        expected_recovery_value = 0.0

        log_recovered_amount = 0.0

        log_pending_amount = 0.0

        log_escalated_amount = 0.0

        log_stopped_amount = 0.0

        for log in logs:

            erv = float(
                log.get(
                    "expected_recovery_value",
                    0
                ) or 0
            )

            amount_recovered = float(
                log.get(
                    "amount_recovered",
                    0
                ) or 0
            )

            expected_recovery_value += erv

            log_recovered_amount += amount_recovered

            final_status = str(
                log.get(
                    "final_status",
                    ""
                )
            ).upper()

            if final_status == "PAYMENT_PENDING":

                log_pending_amount += amount_recovered

            elif final_status == "ESCALATE":

                log_escalated_amount += amount_recovered

            elif final_status == "STOPPED":

                log_stopped_amount += amount_recovered

        # -----------------------------------------------------
        # PENDING TRANSACTIONS
        # -----------------------------------------------------

        for transaction in transactions:

            status = str(
                transaction.status or ""
            ).upper()

            amount = float(
                transaction.amount or 0
            )

            if status in {
                "PAYMENT_PENDING",
                "PENDING"
            }:

                pending_transactions += 1

                pending_amount += amount

        # -----------------------------------------------------
        # STOPPED / ESCALATED
        # -----------------------------------------------------

        for log in logs:

            final_status = str(
                log.get(
                    "final_status",
                    ""
                )
            ).upper()

            transaction_id = log.get(
                "transaction_id"
            )

            transaction = (
                db.query(Transaction)
                .filter(
                    Transaction.transaction_id ==
                    transaction_id
                )
                .first()
            )

            if not transaction:
                continue

            amount = float(
                transaction.amount or 0
            )

            if final_status == "STOPPED":

                stopped_amount += amount

            elif final_status == "ESCALATE":

                escalated_amount += amount

        # -----------------------------------------------------
        # RECOVERY RATE
        # -----------------------------------------------------

        if total_transactions > 0:

            recovery_rate = (
                recovered_transactions
                / total_transactions
            ) * 100

        else:

            recovery_rate = 0.0

        # -----------------------------------------------------
        # REVENUE RECOVERY RATE
        # -----------------------------------------------------

        if total_revenue_at_risk > 0:

            revenue_recovery_rate = (
                total_amount_recovered
                / total_revenue_at_risk
            ) * 100

        else:

            revenue_recovery_rate = 0.0

        # -----------------------------------------------------
        # RETURN METRICS
        # -----------------------------------------------------

        return {

            "total_transactions":
                total_transactions,

            "total_revenue_at_risk":
                round(
                    total_revenue_at_risk,
                    2
                ),

            "expected_recovery_value":
                round(
                    expected_recovery_value,
                    2
                ),

            "total_amount_recovered":
                round(
                    total_amount_recovered,
                    2
                ),

            "recovery_rate":
                round(
                    recovery_rate,
                    2
                ),

            "revenue_recovery_rate":
                round(
                    revenue_recovery_rate,
                    2
                ),

            "pending_amount":
                round(
                    pending_amount,
                    2
                ),

            "escalated_amount":
                round(
                    escalated_amount,
                    2
                ),

            "stopped_amount":
                round(
                    stopped_amount,
                    2
                ),

            "failed_amount":
                round(
                    failed_amount,
                    2
                ),

            "recovered_transactions":
                recovered_transactions,

            "pending_transactions":
                pending_transactions,

            "escalated_transactions":
                escalated_transactions,

            "stopped_transactions":
                stopped_transactions,

            "failed_transactions":
                failed_transactions
        }

    finally:

        db.close()