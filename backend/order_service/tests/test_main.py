import logging
import time
from unittest.mock import AsyncMock, patch

import pytest
from app.db import SessionLocal, engine, get_db
from app.main import app
from app.models import Base, Order, OrderItem  # kept if you use them elsewhere
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

# Suppress noisy logs from SQLAlchemy/FastAPI/Uvicorn during tests for cleaner output
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)
logging.getLogger("app.main").setLevel(logging.WARNING)


@pytest.fixture(scope="session", autouse=True)
def setup_database_for_tests():
    max_retries = 10
    retry_delay_seconds = 3
    for i in range(max_retries):
        try:
            logging.info(
                "Order Service Tests: Attempting to connect to PostgreSQL for test setup (attempt %s/%s)...",
                i + 1,
                max_retries,
            )
            Base.metadata.drop_all(bind=engine)
            logging.info("Order Service Tests: Successfully dropped all tables for test setup.")
            Base.metadata.create_all(bind=engine)
            logging.info("Order Service Tests: Successfully created all tables for test setup.")
            break
        except OperationalError as e:
            logging.warning(
                "Order Service Tests: Test setup DB connection failed: %s. Retrying in %s seconds...",
                e,
                retry_delay_seconds,
            )
            time.sleep(retry_delay_seconds)
            if i == max_retries - 1:
                pytest.fail(
                    f"Could not connect to PostgreSQL for Order Service test setup after {max_retries} attempts: {e}"
                )
        except Exception as e:
            pytest.fail(f"Order Service Tests: Unexpected error during test DB setup: {e}", pytrace=True)

    yield


@pytest.fixture(scope="function")
def db_session_for_test():
    connection = engine.connect()
    transaction = connection.begin()
    db = SessionLocal(bind=connection)

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield db
    finally:
        transaction.rollback()
        db.close()
        connection.close()
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def mock_httpx_client():
    with patch("app.main.httpx.AsyncClient") as mock_async_client_cls:
        mock_client_instance = AsyncMock()
        mock_async_client_cls.return_value.__aenter__.return_value = mock_client_instance
        yield mock_client_instance


def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Order Service!"}


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "order-service"}