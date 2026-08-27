from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


# ============================================================
# CUSTOMER
# ============================================================

class Customer(Base):

    __tablename__ = "customers"

    customer_id = Column(
        String,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        nullable=False
    )

    total_transactions = Column(
        Integer,
        default=0
    )

    successful_transactions = Column(
        Integer,
        default=0
    )

    failed_transactions = Column(
        Integer,
        default=0
    )

    transactions = relationship(
        "Transaction",
        back_populates="customer"
    )


# ============================================================
# TRANSACTION
# ============================================================

class Transaction(Base):

    __tablename__ = "transactions"

    transaction_id = Column(
        String,
        primary_key=True,
        index=True
    )

    customer_id = Column(
        String,
        ForeignKey("customers.customer_id"),
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    currency = Column(
        String,
        default="INR"
    )

    status = Column(
        String,
        default="FAILED"
    )

    payment_method = Column(
        String,
        nullable=False
    )

    failure_reason = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    retry_count = Column(
        Integer,
        default=0,
        nullable=False
    )

    recovery_attempts = Column(
        Integer,
        default=0,
        nullable=False
    )

    last_action = Column(
        String,
        nullable=True
    )

    last_attempt_at = Column(
        DateTime,
        nullable=True
    )

    customer = relationship(
        "Customer",
        back_populates="transactions"
    )

    recovery_attempts_records = relationship(
        "RecoveryAttempt",
        back_populates="transaction"
    )


# ============================================================
# RECOVERY ATTEMPT
# ============================================================

class RecoveryAttempt(Base):

    __tablename__ = "recovery_attempts"

    attempt_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    transaction_id = Column(
        String,
        ForeignKey("transactions.transaction_id"),
        nullable=False,
        index=True
    )

    action = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )

    idempotency_key = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    transaction = relationship(
        "Transaction",
        back_populates="recovery_attempts_records"
    )


# ============================================================
# RECOVERY LOG
# ============================================================

class RecoveryLog(Base):

    __tablename__ = "recovery_logs"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    transaction_id = Column(
        String,
        nullable=False,
        index=True
    )

    action = Column(
        String,
        nullable=True
    )

    recovery_probability = Column(
        Float,
        nullable=True
    )

    expected_recovery_value = Column(
        Float,
        nullable=True
    )

    policy_decision = Column(
        String,
        nullable=True
    )

    execution_status = Column(
        String,
        nullable=True
    )

    verification_status = Column(
        String,
        nullable=True
    )

    final_status = Column(
        String,
        nullable=True
    )

    amount_recovered = Column(
        Float,
        default=0
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )