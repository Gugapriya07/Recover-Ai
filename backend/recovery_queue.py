from database import SessionLocal
from models import Transaction
from retry_manager import get_retry_count


def calculate_priority(transaction, retry_count):

    amount = float(transaction.amount)

    score = amount

    if amount >= 10000:
        score += 5000
    elif amount >= 5000:
        score += 2500
    elif amount >= 2000:
        score += 1000

    score += retry_count * 500

    if transaction.failure_reason == "AUTHENTICATION_FAILED":
        score += 0

    elif transaction.failure_reason == "BANK_DECLINED":
        score += 0

    elif transaction.failure_reason == "CARD_EXPIRED":
        score += 1000

    elif transaction.failure_reason == "INSUFFICIENT_FUNDS":
        score += 0

    if score >= 15000:
        priority = "CRITICAL"
    elif score >= 7000:
        priority = "HIGH"
    elif score >= 3000:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return priority, int(score)


def build_recovery_queue():

    db = SessionLocal()

    try:

        transactions = (
            db.query(Transaction)
            .filter(
                Transaction.status == "FAILED"
            )
            .all()
        )

        queue = []

        for transaction in transactions:

            retry_count = get_retry_count(
                transaction.transaction_id
            )

            priority, priority_score = calculate_priority(
                transaction,
                retry_count
            )

            queue.append({
                "transaction_id":
                    transaction.transaction_id,

                "customer_id":
                    transaction.customer_id,

                "amount":
                    transaction.amount,

                "failure_reason":
                    transaction.failure_reason,

                "payment_method":
                    transaction.payment_method,

                "retry_count":
                    retry_count,

                "priority":
                    priority,

                "priority_score":
                    priority_score
            })

        queue.sort(
            key=lambda x: x["priority_score"],
            reverse=True
        )

        return {
            "queue_size": len(queue),
            "queue": queue
        }

    finally:
        db.close()