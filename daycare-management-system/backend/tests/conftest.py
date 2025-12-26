# Test Configuration and Fixtures
# ============================================

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.child import Child, Parent, ChildParent
from app.core.config import settings


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        first_name="Test",
        last_name="User",
        role="staff",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin(db) -> User:
    """Create a test admin user"""
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("adminpass123"),
        first_name="Admin",
        last_name="User",
        role="admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def auth_headers(client, test_user) -> dict:
    """Get authentication headers for test user"""
    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpass123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_headers(client, test_admin) -> dict:
    """Get authentication headers for admin user"""
    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        data={
            "username": "admin@example.com",
            "password": "adminpass123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def test_child(db) -> Child:
    """Create a test child"""
    from datetime import date
    child = Child(
        first_name="Emma",
        last_name="Johnson",
        date_of_birth=date(2020, 5, 15),
        gender="female",
        enrollment_date=date(2024, 1, 10),
        is_active=True
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return child


@pytest.fixture(scope="function")
def test_parent(db) -> Parent:
    """Create a test parent"""
    parent = Parent(
        first_name="Jane",
        last_name="Johnson",
        email="jane.johnson@example.com",
        phone_primary="555-0123",
        address_street="123 Main St",
        address_city="Chicago",
        address_state="IL",
        address_zip="60601"
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)
    return parent


@pytest.fixture(scope="function")
def test_child_with_parent(db, test_child, test_parent) -> Child:
    """Create a child with parent relationship"""
    child_parent = ChildParent(
        child_id=test_child.id,
        parent_id=test_parent.id,
        relationship_type="mother",
        is_primary_contact=True,
        is_authorized_pickup=True,
        has_legal_custody=True
    )
    db.add(child_parent)
    db.commit()
    return test_child
