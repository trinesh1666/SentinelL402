from datetime import datetime, timedelta, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    email = Column(
        String,
        unique=True,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    account = relationship(
        "Account",
        back_populates="user",
        uselist=False,
    )

    api_keys = relationship(
        "APIKey",
        back_populates="user",
    )


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    key_hash = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String,
        nullable=True,
    )

    active = Column(
        Integer,
        default=1,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    last_used_at = Column(
        DateTime,
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="api_keys",
    )


class Account(Base):
    __tablename__ = "accounts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
    Integer,
    ForeignKey("users.id"),
    nullable=False,
    unique=True,
)

    credits = Column(
        Integer,
        default=5,
    )

    total_requests = Column(
        Integer,
        default=0,
    )

    user = relationship(
        "User",
        back_populates="account",
    )


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    request_type = Column(
        String,
        default="ai_analysis",
    )

    credits_used = Column(
        Integer,
        default=1,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    amount_sats = Column(Integer, nullable=False)

    payment_hash = Column(
        String,
        unique=True,
        nullable=True,
    )

    status = Column(String, default="pending")

    invoice = Column(
        String,
        unique=True,
        nullable=True,
    )

    credits_granted = Column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    expires_at = Column(
    DateTime,
    nullable=True,
    )
    description = Column(String, nullable=True)