from erv_engine import calculate_expected_recovery_value


result = calculate_expected_recovery_value(
    amount=2499,
    recovery_probability=70,
    action_cost=20
)

print(result)