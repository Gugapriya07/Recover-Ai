from database import SessionLocal
from models import Customer, Transaction

db = SessionLocal()

customers = db.query(Customer).all()
transactions = db.query(Transaction).all()

print("\nCUSTOMERS")
for customer in customers:
    print(
        customer.customer_id,
        customer.name,
        customer.total_transactions,
        customer.successful_transactions,
        customer.failed_transactions
    )

print("\nTRANSACTIONS")
for transaction in transactions:
    print(
        transaction.transaction_id,
        transaction.customer_id,
        transaction.amount,
        transaction.status,
        transaction.failure_reason
    )

db.close()