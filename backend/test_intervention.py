from intervention_engine import choose_intervention


result = choose_intervention(
    failure_reason="INSUFFICIENT_FUNDS",
    recovery_probability=75,
    expected_recovery_value=1600,
    amount=2499
)

print(result)