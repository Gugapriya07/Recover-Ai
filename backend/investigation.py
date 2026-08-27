from database import SessionLocal
from models import Transaction, Customer

from ml.recovery_predictor import (
    predict_recovery_probability
)


def investigate_payment(transaction_id):

    db = SessionLocal()

    try:

        transaction = (
            db.query(Transaction)
            .filter(
                Transaction.transaction_id == transaction_id
            )
            .first()
        )

        if not transaction:

            return {
                "error": "Transaction not found."
            }


        # -------------------------------------------------
        # CUSTOMER
        # -------------------------------------------------

        customer = None

        if hasattr(transaction, "customer_id"):

            customer = (
                db.query(Customer)
                .filter(
                    Customer.customer_id ==
                    transaction.customer_id
                )
                .first()
            )


        # -------------------------------------------------
        # CUSTOMER HISTORY
        # -------------------------------------------------

        total_transactions = 0
        successful_transactions = 0
        failed_transactions = 0

        previous_successes = 0

        if customer:

            customer_transactions = (
                db.query(Transaction)
                .filter(
                    Transaction.customer_id ==
                    customer.customer_id
                )
                .all()
            )

            total_transactions = len(
                customer_transactions
            )

            successful_transactions = sum(
                1
                for t in customer_transactions
                if str(t.status).upper()
                in ["SUCCESS", "RECOVERED"]
            )

            failed_transactions = sum(
                1
                for t in customer_transactions
                if str(t.status).upper()
                == "FAILED"
            )

            previous_successes = successful_transactions


        # -------------------------------------------------
        # SUCCESS RATE
        # -------------------------------------------------

        if total_transactions > 0:

            success_rate = round(
                (
                    successful_transactions
                    / total_transactions
                ) * 100,
                2
            )

        else:

            success_rate = 0.0


        # -------------------------------------------------
        # BASIC TRANSACTION DATA
        # -------------------------------------------------

        amount = float(
            transaction.amount or 0
        )

        payment_method = (
            transaction.payment_method
            or "UNKNOWN"
        )

        failure_reason = (
            transaction.failure_reason
            or "UNKNOWN"
        )


        # -------------------------------------------------
        # ML RECOVERY PROBABILITY
        # -------------------------------------------------

        recovery_probability = (
            predict_recovery_probability(

                amount=amount,

                customer_success_rate=
                    success_rate,

                failure_reason=
                    failure_reason,

                payment_method=
                    payment_method,

                previous_successes=
                    previous_successes
            )
        )


        # -------------------------------------------------
        # RECOVERABILITY
        # -------------------------------------------------

        if recovery_probability >= 70:

            recoverability = "HIGH"

        elif recovery_probability >= 40:

            recoverability = "MEDIUM"

        else:

            recoverability = "LOW"


        # -------------------------------------------------
        # RECOMMENDATION
        # -------------------------------------------------

        if recovery_probability >= 70:

            recommendation = "RETRY_PAYMENT"

        elif recovery_probability >= 40:

            recommendation = "TRY_ALTERNATIVE_PAYMENT"

        else:

            recommendation = "ESCALATE"


        # -------------------------------------------------
        # REASON
        # -------------------------------------------------

        reason = (
            f"ML model estimated a "
            f"{recovery_probability}% recovery probability "
            f"for {failure_reason}. "
            f"Customer historical success rate is "
            f"{success_rate}%."
        )


        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        return {

            "transaction": {

                "transaction_id":
                    transaction.transaction_id,

                "amount":
                    amount,

                "currency":
                    getattr(
                        transaction,
                        "currency",
                        "INR"
                    ),

                "payment_method":
                    payment_method,

                "status":
                    transaction.status,

                "failure_reason":
                    failure_reason
            },

            "customer": {

                "customer_id":
                    getattr(
                        customer,
                        "customer_id",
                        getattr(
                            transaction,
                            "customer_id",
                            None
                        )
                    ),

                "name":
                    getattr(
                        customer,
                        "name",
                        "Unknown"
                    ),

                "email":
                    getattr(
                        customer,
                        "email",
                        ""
                    )
            },

            "customer_history": {

                "total_transactions":
                    total_transactions,

                "successful_transactions":
                    successful_transactions,

                "failed_transactions":
                    failed_transactions,

                "success_rate":
                    success_rate,

                "previous_successes":
                    previous_successes
            },

            "investigation": {

                "recoverability":
                    recoverability,

                "recovery_probability":
                    recovery_probability,

                "recommendation":
                    recommendation,

                "reason":
                    reason
            },

            "recovery_probability":
                recovery_probability
        }

    finally:

        db.close()