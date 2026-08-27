# =========================================================
# PROJECT PATH
# =========================================================

import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# =========================================================
# IMPORTS
# =========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal
from models import Transaction, RecoveryLog

from recovery_agent import run_recovery_agent
from recovery_log import get_recovery_logs


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="RecoverAI",
    description="Autonomous Payment Recovery Agent",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "project": "RecoverAI",
        "description": "Autonomous Payment Recovery Agent",
        "status": "running"
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================================================
# DATABASE
# =========================================================

@app.get("/database")
def database_status():

    db = SessionLocal()

    try:

        transaction_count = (
            db.query(Transaction).count()
        )

        recovery_log_count = (
            db.query(RecoveryLog).count()
        )

        return {
            "database": "connected",
            "transactions": transaction_count,
            "recovery_logs": recovery_log_count
        }

    finally:

        db.close()


# =========================================================
# ANALYZE TRANSACTION
# =========================================================

@app.get("/analyze/{transaction_id}")
def analyze_transaction(
    transaction_id: str
):

    return run_recovery_agent(
        transaction_id
    )


# =========================================================
# AGENT RECOVERY
# =========================================================

@app.get("/agent/recover/{transaction_id}")
def recover_transaction(
    transaction_id: str
):

    return run_recovery_agent(
        transaction_id
    )


# =========================================================
# RECOVERY LOGS
# =========================================================

@app.get("/recovery-logs")
def recovery_logs():

    return get_recovery_logs()


# =========================================================
# METRICS
# =========================================================

@app.get("/metrics")
def metrics():

    db = SessionLocal()

    try:

        transactions = (
            db.query(Transaction).all()
        )

        logs = (
            db.query(RecoveryLog).all()
        )

        # -------------------------------------------------
        # BASIC COUNTS
        # -------------------------------------------------

        total_transactions = len(
            transactions
        )

        total_revenue_at_risk = sum(
            float(t.amount or 0)
            for t in transactions
            if str(t.status).upper()
            not in [
                "SUCCESS",
                "RECOVERED"
            ]
        )

        total_amount_recovered = sum(
            float(log.amount_recovered or 0)
            for log in logs
        )

        expected_recovery_value = sum(
            float(log.expected_recovery_value or 0)
            for log in logs
        )

        # -------------------------------------------------
        # TRANSACTION STATUS
        # -------------------------------------------------

        recovered_transactions = sum(
            1
            for t in transactions
            if str(t.status).upper()
            in [
                "SUCCESS",
                "RECOVERED"
            ]
        )

        pending_transactions = sum(
            1
            for t in transactions
            if str(t.status).upper()
            in [
                "PAYMENT_PENDING",
                "PENDING"
            ]
        )

        failed_transactions = sum(
            1
            for t in transactions
            if str(t.status).upper()
            == "FAILED"
        )

        # -------------------------------------------------
        # LOG STATUS
        # -------------------------------------------------

        stopped_transactions = sum(
            1
            for log in logs
            if str(log.final_status).upper()
            in [
                "STOPPED",
                "STOP"
            ]
        )

        escalated_transactions = sum(
            1
            for log in logs
            if str(log.final_status).upper()
            == "ESCALATE"
        )

        # -------------------------------------------------
        # AMOUNTS BY STATUS
        # -------------------------------------------------

        pending_amount = sum(
            float(t.amount or 0)
            for t in transactions
            if str(t.status).upper()
            in [
                "PAYMENT_PENDING",
                "PENDING"
            ]
        )

        stopped_amount = sum(
            float(t.amount or 0)
            for t in transactions
            if str(t.status).upper()
            == "STOPPED"
        )

        failed_amount = sum(
            float(t.amount or 0)
            for t in transactions
            if str(t.status).upper()
            == "FAILED"
        )

        escalated_txn_ids = {
            log.transaction_id
            for log in logs
            if str(log.final_status).upper()
            == "ESCALATE"
        }

        escalated_amount = sum(
            float(t.amount or 0)
            for t in transactions
            if t.transaction_id in escalated_txn_ids
        )

        # -------------------------------------------------
        # ACTION PERFORMANCE
        # -------------------------------------------------

        action_metrics = {}

        for log in logs:

            action = (
                log.action
                or "UNKNOWN"
            )

            if action not in action_metrics:

                action_metrics[action] = {
                    "attempts": 0,
                    "recovered": 0,
                    "amount_recovered": 0.0,
                    "expected_recovery_value": 0.0
                }

            action_metrics[action][
                "attempts"
            ] += 1

            action_metrics[action][
                "amount_recovered"
            ] += float(
                log.amount_recovered or 0
            )

            action_metrics[action][
                "expected_recovery_value"
            ] += float(
                log.expected_recovery_value or 0
            )

            if (
                str(
                    log.final_status
                ).upper()
                == "RECOVERED"
            ):

                action_metrics[action][
                    "recovered"
                ] += 1

        # -------------------------------------------------
        # ACTION RECOVERY RATE
        # -------------------------------------------------

        for action, data in (
            action_metrics.items()
        ):

            attempts = data["attempts"]

            if attempts > 0:

                data["recovery_rate"] = round(
                    (
                        data["recovered"]
                        / attempts
                    ) * 100,
                    2
                )

            else:

                data["recovery_rate"] = 0.0

        # -------------------------------------------------
        # FAILURE REASON METRICS
        # -------------------------------------------------

        failure_reason_metrics = {}

        for transaction in transactions:

            reason = (
                transaction.failure_reason
                or "UNKNOWN"
            )

            if reason not in failure_reason_metrics:

                failure_reason_metrics[reason] = {
                    "transactions": 0,
                    "revenue_at_risk": 0.0
                }

            if (
                str(
                    transaction.status
                ).upper()
                not in [
                    "SUCCESS",
                    "RECOVERED"
                ]
            ):

                failure_reason_metrics[reason][
                    "transactions"
                ] += 1

                failure_reason_metrics[reason][
                    "revenue_at_risk"
                ] += float(
                    transaction.amount or 0
                )

        # -------------------------------------------------
        # RECOVERY RATE
        # -------------------------------------------------

        if total_transactions > 0:

            recovery_rate = round(
                (
                    recovered_transactions
                    / total_transactions
                ) * 100,
                2
            )

        else:

            recovery_rate = 0.0

        # -------------------------------------------------
        # REVENUE RECOVERY RATE
        # -------------------------------------------------

        total_revenue_processed = (
            total_revenue_at_risk
            + total_amount_recovered
        )

        if total_revenue_processed > 0:

            revenue_recovery_rate = round(
                (
                    total_amount_recovered
                    / total_revenue_processed
                ) * 100,
                2
            )

        else:

            revenue_recovery_rate = 0.0

        # -------------------------------------------------
        # FINAL RESPONSE
        # -------------------------------------------------

        return {

            "total_transactions":
                total_transactions,

            "total_revenue_at_risk":
                round(
                    total_revenue_at_risk,
                    2
                ),

            "expected_recovery_value":
                round(
                    expected_recovery_value,
                    2
                ),

            "total_amount_recovered":
                round(
                    total_amount_recovered,
                    2
                ),

            "recovery_rate":
                recovery_rate,

            "revenue_recovery_rate":
                revenue_recovery_rate,

            "pending_amount":
                round(
                    pending_amount,
                    2
                ),

            "escalated_amount":
                round(
                    escalated_amount,
                    2
                ),

            "stopped_amount":
                round(
                    stopped_amount,
                    2
                ),

            "failed_amount":
                round(
                    failed_amount,
                    2
                ),

            "recovered_transactions":
                recovered_transactions,

            "pending_transactions":
                pending_transactions,

            "escalated_transactions":
                escalated_transactions,

            "stopped_transactions":
                stopped_transactions,

            "failed_transactions":
                failed_transactions,

            "action_metrics":
                action_metrics,

            "failure_reason_metrics":
                failure_reason_metrics
        }

    finally:

        db.close()