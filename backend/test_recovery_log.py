from recovery_log import log_recovery_decision, get_recovery_logs


log_recovery_decision(
    transaction_id="TXN_1001",
    action="WAIT_AND_RETRY",
    probability=75,
    erv=1600,
    policy_decision="APPROVE",
    execution_status="SCHEDULED",
    verification_status="PENDING",
    final_status="RECOVERY_PENDING"
)

print(get_recovery_logs())