import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.middleware.database_errors import (
    DatabaseServiceError,
)
from app.services import payment_service


class FakeCommitFailure(SQLAlchemyError):
    """Simulated SQLAlchemy commit failure."""


class FakeQuery:
    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return None


def test_create_payment_rolls_back_on_database_failure(
    monkeypatch,
):
    rollback_called = False

    class FakeDB:
        def add(self, obj):
            pass

        def commit(self):
            raise FakeCommitFailure(
                "SECRET_DATABASE_FAILURE"
            )

        def rollback(self):
            nonlocal rollback_called
            rollback_called = True

        def refresh(self, obj):
            pass

        def query(self, model):
            return FakeQuery()

    monkeypatch.setattr(
        payment_service,
        "create_lightning_invoice",
        lambda amount, description: type(
            "Invoice",
            (),
            {
                "invoice": "lnbc_test",
                "payment_hash": "hash_test",
            },
        )(),
    )

    from app.models import User

    db = FakeDB()

    def fake_get_or_create_user(db, user_id):
        return User(
            id=1,
            user_id=user_id,
        )

    monkeypatch.setattr(
        "app.services.metering_service.get_or_create_user",
        fake_get_or_create_user,
    )

    with pytest.raises(DatabaseServiceError) as exc_info:
        payment_service.create_payment(
            db,
            "transaction-test-user",
        )

    assert str(exc_info.value) == "Failed to save payment."
    assert rollback_called is True