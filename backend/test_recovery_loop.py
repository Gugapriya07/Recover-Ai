from recovery_loop import run_recovery_attempt


result = run_recovery_attempt(
    transaction_id="TXN_1001",
    action="RETRY_PAYMENT",
    amount=2499,
    payment_method="UPI",
    recovery_probability=80
)

print(result)