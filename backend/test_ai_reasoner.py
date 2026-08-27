from ai_reasoner import generate_recovery_explanation


result = generate_recovery_explanation(
    transaction_id="TXN_1001",
    amount=2499,
    failure_reason="INSUFFICIENT_FUNDS",
    payment_method="UPI",
    recovery_probability=75,
    expected_recovery_value=1854,
    recommended_action="WAIT_AND_RETRY",
    customer_success_rate=80,
    previous_successes=8
)

print(result)