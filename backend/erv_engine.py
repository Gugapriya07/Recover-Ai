def calculate_expected_recovery_value(
    amount,
    recovery_probability,
    action_cost=0
):
    probability = recovery_probability / 100

    expected_recovery = amount * probability

    expected_value = expected_recovery - action_cost

    return {
        "payment_amount": round(amount, 2),
        "recovery_probability": round(recovery_probability, 2),
        "expected_recovery": round(expected_recovery, 2),
        "action_cost": round(action_cost, 2),
        "expected_recovery_value": round(expected_value, 2)
    }