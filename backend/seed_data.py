from database import SessionLocal, engine, Base
from models import Customer, Transaction


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# SEED DATA
# =========================================================

def seed_data():

    db = SessionLocal()

    try:

        # -------------------------------------------------
        # PREVENT DUPLICATE DATA
        # -------------------------------------------------

        if db.query(Customer).count() > 0:

            print("Data already exists.")
            return


        # =================================================
        # CUSTOMERS
        # =================================================

        customers = [

            Customer(
                customer_id="CUST_001",
                name="Arun Kumar",
                email="arun@example.com"
            ),

            Customer(
                customer_id="CUST_002",
                name="Priya Sharma",
                email="priya@example.com"
            ),

            Customer(
                customer_id="CUST_003",
                name="Rahul Das",
                email="rahul@example.com"
            ),

            Customer(
                customer_id="CUST_004",
                name="Sneha Rao",
                email="sneha@example.com"
            ),

            Customer(
                customer_id="CUST_005",
                name="Vikram Singh",
                email="vikram@example.com"
            ),

            Customer(
                customer_id="CUST_006",
                name="Karthik Raj",
                email="karthik@example.com"
            ),

            Customer(
                customer_id="CUST_007",
                name="Meera Iyer",
                email="meera@example.com"
            ),

            Customer(
                customer_id="CUST_008",
                name="Aditya Menon",
                email="aditya@example.com"
            ),

            Customer(
                customer_id="CUST_009",
                name="Nisha Patel",
                email="nisha@example.com"
            ),

            Customer(
                customer_id="CUST_010",
                name="Rohan Verma",
                email="rohan@example.com"
            )
        ]

        db.add_all(customers)
        db.commit()


        # =================================================
        # TRANSACTIONS
        # =================================================

        transactions = [

            # -------------------------------------------------
            # CUSTOMER 001
            # -------------------------------------------------

            Transaction(
                transaction_id="TXN_1001",
                customer_id="CUST_001",
                amount=2499,
                currency="INR",
                status="FAILED",
                payment_method="UPI",
                failure_reason="INSUFFICIENT_FUNDS"
            ),

            Transaction(
                transaction_id="TXN_1002",
                customer_id="CUST_001",
                amount=999,
                currency="INR",
                status="SUCCESS",
                payment_method="UPI"
            ),

            Transaction(
                transaction_id="TXN_1003",
                customer_id="CUST_001",
                amount=1799,
                currency="INR",
                status="FAILED",
                payment_method="UPI",
                failure_reason="UPI_TIMEOUT"
            ),


            # -------------------------------------------------
            # CUSTOMER 002
            # -------------------------------------------------

            Transaction(
                transaction_id="TXN_1004",
                customer_id="CUST_002",
                amount=5499,
                currency="INR",
                status="FAILED",
                payment_method="CREDIT_CARD",
                failure_reason="CARD_EXPIRED"
            ),

            Transaction(
                transaction_id="TXN_1005",
                customer_id="CUST_002",
                amount=1499,
                currency="INR",
                status="SUCCESS",
                payment_method="CREDIT_CARD"
            ),

            Transaction(
                transaction_id="TXN_1006",
                customer_id="CUST_002",
                amount=3299,
                currency="INR",
                status="FAILED",
                payment_method="CREDIT_CARD",
                failure_reason="AUTHENTICATION_FAILED"
            ),


            # -------------------------------------------------
            # CUSTOMER 003
            # -------------------------------------------------

            Transaction(
                transaction_id="TXN_1007",
                customer_id="CUST_003",
                amount=7999,
                currency="INR",
                status="FAILED",
                payment_method="DEBIT_CARD",
                failure_reason="BANK_DECLINED"
            ),

            Transaction(
                transaction_id="TXN_1008",
                customer_id="CUST_003",
                amount=2999,
                currency="INR",
                status="SUCCESS",
                payment_method="UPI"
            ),

            Transaction(
                transaction_id="TXN_1009",
                customer_id="CUST_003",
                amount=1299,
                currency="INR",
                status="FAILED",
                payment_method="UPI",
                failure_reason="INSUFFICIENT_FUNDS"
            ),


            # -------------------------------------------------
            # CUSTOMER 004
            # -------------------------------------------------

            Transaction(
                transaction_id="TXN_1010",
                customer_id="CUST_004",
                amount=1999,
                currency="INR",
                status="FAILED",
                payment_method="UPI",
                failure_reason="UPI_TIMEOUT"
            ),

            Transaction(
                transaction_id="TXN_1011",
                customer_id="CUST_004",
                amount=4999,
                currency="INR",
                status="SUCCESS",
                payment_method="UPI"
            ),

            Transaction(
                transaction_id="TXN_1012",
                customer_id="CUST_004",
                amount=2599,
                currency="INR",
                status="FAILED",
                payment_method="UPI",
                failure_reason="PAYMENT_FAILED"
            ),


            # -------------------------------------------------
            # CUSTOMER 005
            # -------------------------------------------------

            Transaction(
                transaction_id="TXN_1013",
                customer_id="CUST_005",
                amount=12999,
                currency="INR",
                status="FAILED",
                payment_method="CREDIT_CARD",
                failure_reason="AUTHENTICATION_FAILED"
            ),

            Transaction(
                transaction_id="TXN_1014",
                customer_id="CUST_005",
                amount=3999,
                currency="INR",
                status="SUCCESS",
                payment_method="CREDIT_CARD"
            ),

            Transaction(
                transaction_id="TXN_1015",
                customer_id="CUST_005",
                amount=2199,
                currency="INR",
                status="FAILED",
                payment_method="CREDIT_CARD",
                failure_reason="CARD_EXPIRED"
            ),


            # -------------------------------------------------
            # CUSTOMER 006
            # -------------------------------------------------

            Transaction(
                transaction_id="TXN_1016",
                customer_id="CUST_006",
                amount=899,
                currency="INR",
                status="SUCCESS",
                payment_method="UPI"
            ),

            Transaction(
                transaction_id="TXN_1017",
                customer_id="CUST_006",
                amount=1899,
                currency="INR",
                status="FAILED",
                payment_method="UPI",
                failure_reason="UPI_TIMEOUT"
            ),


            # -------------------------------------------------
            # CUSTOMER 007
            # -------------------------------------------------

            Transaction(
                transaction_id="TXN_1018",
                customer_id="CUST_007",
                amount=6499,
                currency="INR",
                status="SUCCESS",
                payment_method="CREDIT_CARD"
            ),

            Transaction(
                transaction_id="TXN_1019",
                customer_id="CUST_007",
                amount=7499,
                currency="INR",
                status="FAILED",
                payment_method="CREDIT_CARD",
                failure_reason="BANK_DECLINED"
            ),

            Transaction(
                transaction_id="TXN_1020",
                customer_id="CUST_007",
                amount=1499,
                currency="INR",
                status="FAILED",
                payment_method="CREDIT_CARD",
                failure_reason="AUTHENTICATION_FAILED"
            ),


            # -------------------------------------------------
            # CUSTOMER 008
            # -------------------------------------------------

            Transaction(
                transaction_id="TXN_1021",
                customer_id="CUST_008",
                amount=9999,
                currency="INR",
                status="SUCCESS",
                payment_method="DEBIT_CARD"
            ),

            Transaction(
                transaction_id="TXN_1022",
                customer_id="CUST_008",
                amount=1199,
                currency="INR",
                status="FAILED",
                payment_method="DEBIT_CARD",
                failure_reason="INSUFFICIENT_FUNDS"
            ),


            # -------------------------------------------------
            # CUSTOMER 009
            # -------------------------------------------------

            Transaction(
                transaction_id="TXN_1023",
                customer_id="CUST_009",
                amount=4599,
                currency="INR",
                status="SUCCESS",
                payment_method="UPI"
            ),

            # Additional history: CUST_009 is a loyal, high-trust
            # customer with a strong prior payment record, which
            # is what should let a large failed payment clear the
            # probability/ERV checks and reach the amount-ceiling
            # policy (-> ESCALATE) instead of being auto-stopped.

            Transaction(
                transaction_id="TXN_1023B",
                customer_id="CUST_009",
                amount=6200,
                currency="INR",
                status="SUCCESS",
                payment_method="UPI"
            ),

            Transaction(
                transaction_id="TXN_1023C",
                customer_id="CUST_009",
                amount=3100,
                currency="INR",
                status="SUCCESS",
                payment_method="UPI"
            ),

            Transaction(
                transaction_id="TXN_1024",
                customer_id="CUST_009",
                amount=3599,
                currency="INR",
                status="FAILED",
                payment_method="UPI",
                failure_reason="UPI_TIMEOUT"
            ),


            # -------------------------------------------------
            # CUSTOMER 010
            # -------------------------------------------------

            Transaction(
                transaction_id="TXN_1025",
                customer_id="CUST_010",
                amount=15999,
                currency="INR",
                status="FAILED",
                payment_method="CREDIT_CARD",
                failure_reason="BANK_DECLINED"
            ),

            # -------------------------------------------------
            # HIGH-VALUE TRANSACTION
            # Amount exceeds MAX_AUTONOMOUS_AMOUNT (10,000)
            # and has a strong recovery signal (UPI_TIMEOUT,
            # good customer history), so it should clear
            # probability/ERV checks and hit the amount-ceiling
            # policy -> ESCALATE to manual review.
            # -------------------------------------------------

            Transaction(
                transaction_id="TXN_1026",
                customer_id="CUST_009",
                amount=24999,
                currency="INR",
                status="FAILED",
                payment_method="UPI",
                failure_reason="UPI_TIMEOUT"
            )

        ]


        db.add_all(transactions)
        db.commit()


        # =================================================
        # UPDATE CUSTOMER STATISTICS
        # =================================================

        for customer in customers:

            customer_transactions = (
                db.query(Transaction)
                .filter(
                    Transaction.customer_id
                    == customer.customer_id
                )
                .all()
            )

            customer.total_transactions = (
                len(customer_transactions)
            )

            customer.successful_transactions = sum(
                1
                for transaction in customer_transactions
                if transaction.status == "SUCCESS"
            )

            customer.failed_transactions = sum(
                1
                for transaction in customer_transactions
                if transaction.status == "FAILED"
            )


        db.commit()

        print(
            "Successfully seeded RecoverAI database!"
        )

        print(
            f"Customers: {len(customers)}"
        )

        print(
            f"Transactions: {len(transactions)}"
        )

        print(
            "Failed transactions:",
            sum(
                1
                for transaction in transactions
                if transaction.status == "FAILED"
            )
        )

        print(
            "Successful transactions:",
            sum(
                1
                for transaction in transactions
                if transaction.status == "SUCCESS"
            )
        )


    except Exception as e:

        db.rollback()

        print(
            f"Error while seeding database: {e}"
        )

        raise


    finally:

        db.close()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    seed_data()