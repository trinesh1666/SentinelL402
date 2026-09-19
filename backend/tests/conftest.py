from pathlib import Path
from unittest.mock import patch

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.services.auth_service import get_authenticated_user


TEST_DB_PATH = (
    Path(__file__).resolve().parent
    / "test_sentinell402.db"
)

TEST_DATABASE_URL = (
    f"sqlite:///{TEST_DB_PATH}"
)


test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=NullPool,
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

@pytest.fixture()
def mock_ollama():
    """
    Replace external Ollama calls with deterministic
    responses for agent/integration tests.
    """

    def fake_generate_text(prompt: str, model=None):

        # Only inspect the actual user request.
        # Do not inspect the system prompt because it contains
        # security-related keywords by design.
        user_request = prompt.split(
            "User request:",
            1,
        )[-1].strip().lower()

        security_keywords = [
            "network",
            "security",
            "attack",
            "threat",
            "traffic",
            "cybersecurity",
            "intrusion",
            "ddos",
            "firewall",
            "packet",
        ]

        is_security_request = any(
            keyword in user_request
            for keyword in security_keywords
        )

        # Intent classification
        if "routing component of SentinelL402" in prompt:
            if is_security_request:
                return '{"intent":"security"}'

            return '{"intent":"unsupported"}'

        # Tool selection
        if "tool-selection component of SentinelL402" in prompt:
            if is_security_request:
                return (
                    '{"action":"analyze_security",'
                    '"tool":"analyze_network_security",'
                    '"arguments":{},'
                    '"confidence":1.0}'
                )

            return (
                '{"action":"unsupported",'
                '"tool":"none",'
                '"arguments":{},'
                '"confidence":1.0}'
            )

        # Security-analysis LLM response
        return (
            "1. Security Analysis\n"
            "The machine-learning security detector "
            "completed the requested analysis.\n\n"
            "2. Security Risk\n"
            "The risk level is based on the supplied "
            "machine-learning classification.\n\n"
            "3. Recommended Defensive Action\n"
            "Continue monitoring the network activity "
            "and investigate according to the supplied "
            "security classification."
        )

    with patch(
        "app.agent.llm_router.generate_text",
        side_effect=fake_generate_text,
    ), patch(
        "app.services.llm_service.generate_text",
        side_effect=fake_generate_text,
    ):
        yield

@pytest.fixture(
    scope="session",
    autouse=True,
)
def create_test_database():
    Base.metadata.drop_all(
        bind=test_engine
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine
    )

    test_engine.dispose()

    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture()
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()

        if transaction.is_active:
            transaction.rollback()

        connection.close()

@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[
        get_db
    ] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(
        get_db,
        None,
    )

    app.dependency_overrides.pop(
        get_authenticated_user,
        None,
    )