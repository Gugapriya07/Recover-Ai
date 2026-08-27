from enum import Enum


class RecoveryState(str, Enum):

    DETECTED = "DETECTED"

    INVESTIGATING = "INVESTIGATING"

    EVALUATING = "EVALUATING"

    POLICY_CHECK = "POLICY_CHECK"

    EXECUTING = "EXECUTING"

    VERIFYING = "VERIFYING"

    RECOVERED = "RECOVERED"

    RECOVERY_FAILED = "RECOVERY_FAILED"

    ESCALATED = "ESCALATED"

    STOPPED = "STOPPED"


# =========================================================
# ALLOWED TRANSITIONS
# =========================================================

TRANSITIONS = {

    RecoveryState.DETECTED: [
        RecoveryState.INVESTIGATING
    ],

    RecoveryState.INVESTIGATING: [
        RecoveryState.EVALUATING
    ],

    RecoveryState.EVALUATING: [
        RecoveryState.POLICY_CHECK
    ],

    RecoveryState.POLICY_CHECK: [
        RecoveryState.EXECUTING,
        RecoveryState.RECOVERED,
        RecoveryState.STOPPED,
        RecoveryState.ESCALATED
    ],

    RecoveryState.EXECUTING: [
        RecoveryState.VERIFYING,
        RecoveryState.RECOVERY_FAILED
    ],

    RecoveryState.VERIFYING: [
        RecoveryState.RECOVERED,
        RecoveryState.RECOVERY_FAILED,
        RecoveryState.ESCALATED
    ],

    RecoveryState.RECOVERY_FAILED: [
        RecoveryState.EXECUTING,
        RecoveryState.ESCALATED,
        RecoveryState.STOPPED
    ],

    RecoveryState.RECOVERED: [],

    RecoveryState.ESCALATED: [],

    RecoveryState.STOPPED: []
}


def update_state(current_state, next_state):

    try:
        current = RecoveryState(current_state)

    except ValueError:
        raise ValueError(
            f"Unknown current recovery state: {current_state}"
        )

    try:
        next_value = RecoveryState(next_state)

    except ValueError:
        raise ValueError(
            f"Unknown next recovery state: {next_state}"
        )

    allowed_states = TRANSITIONS.get(
        current,
        []
    )

    if next_value not in allowed_states:

        raise ValueError(
            f"Invalid state transition: "
            f"{current.value} -> {next_value.value}"
        )

    return next_value.value


def get_initial_state():

    return RecoveryState.DETECTED.value


def is_terminal_state(state):

    try:
        current = RecoveryState(state)

    except ValueError:
        return False

    return current in {
        RecoveryState.RECOVERED,
        RecoveryState.ESCALATED,
        RecoveryState.STOPPED
    }