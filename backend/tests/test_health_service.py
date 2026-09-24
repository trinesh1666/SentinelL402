from unittest.mock import Mock

from app.services.health_service import check_database


def test_check_database_success():
    db = Mock()

    result = check_database(db)

    assert result is True
    db.execute.assert_called_once()


def test_check_database_failure():
    db = Mock()
    db.execute.side_effect = Exception("database unavailable")

    result = check_database(db)

    assert result is False