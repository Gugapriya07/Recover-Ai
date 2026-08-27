from action_executor import execute_action


result = execute_action(
    action="RETRY_PAYMENT",
    transaction_id="TXN_1001",
    amount=2499,
    payment_method="UPI"
)

print(result)