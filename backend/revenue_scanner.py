from database import SessionLocal
from models import Transaction


def scan_revenue_at_risk():

    db = SessionLocal()

    try:
        transactions = db.query(Transaction).filter(
            Transaction.status == "FAILED"
        ).all()

        total_risk = sum(
            transaction.amount
            for transaction in transactions
        )

        high_value = [
            {
                "transaction_id": t.transaction_id,
                "customer_id": t.customer_id,
                "amount": t.amount,
                "failure_reason": t.failure_reason,
                "payment_method": t.payment_method
            }
            for t in transactions
            if t.amount >= 5000
        ]

        return {
            "failed_transactions": len(transactions),
            "total_revenue_at_risk": round(total_risk, 2),
            "high_value_transactions": high_value
        }

    finally:
        db.close()