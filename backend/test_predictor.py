from recovery_predictor import predict_recovery_probability


probability = predict_recovery_probability(
    amount=2499,
    payment_method="UPI",
    failure_reason="INSUFFICIENT_FUNDS",
    customer_success_rate=50,
    previous_successes=1
)

print(f"Recovery probability: {probability}%")