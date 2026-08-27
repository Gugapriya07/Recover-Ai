from database import SessionLocal
from models import Customer, Transaction


def get_customer_risk(customer_id):

    db = SessionLocal()

    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()

    transactions = db.query(Transaction).filter(
        Transaction.customer_id == customer_id
    ).all()

    db.close()

    if not customer:
        return {
            "error": "Customer not found"
        }

    total = len(transactions)

    successful = sum(
        1
        for t in transactions
        if t.status == "SUCCESS"
    )

    failed = sum(
        1
        for t in transactions
        if t.status == "FAILED"
    )

    success_rate = (
        successful / total * 100
        if total > 0
        else 0
    )

    if success_rate >= 80:
        risk = "LOW"

    elif success_rate >= 50:
        risk = "MEDIUM"

    else:
        risk = "HIGH"

    return {
        "customer_id": customer.customer_id,
        "customer_name": customer.name,
        "email": customer.email,
        "total_transactions": total,
        "successful_transactions": successful,
        "failed_transactions": failed,
        "success_rate": round(success_rate, 2),
        "risk_level": risk
    }