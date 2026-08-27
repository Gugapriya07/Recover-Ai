from verification import verify_payment


result = verify_payment(
    transaction_id="TXN_1001",
    action="RETRY_PAYMENT",
    recovery_probability=80
)

print(result)