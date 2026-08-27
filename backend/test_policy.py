from policy_engine import check_policy


result = check_policy(
    action="WAIT_AND_RETRY",
    amount=2499,
    recovery_probability=75,
    expected_recovery_value=1600,
    retry_count=0,
    payment_status="FAILED",
    failure_reason="INSUFFICIENT_FUNDS"
)

print(result)