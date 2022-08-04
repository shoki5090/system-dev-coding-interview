import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    client = TestClient(app)
    return client

@pytest.fixture
def create_user(test_db, client):
    response = client.post(
        "/users/",
        json={"email": "deadpool@example.com", "password": "chimichangas4life"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    return data

@pytest.fixture
def create_second_user(test_db, client):
    response = client.post(
        "/users/",
        json={"email": "ironman@example.com", "password": "shoyuRamen"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    return data

@pytest.fixture
def dummy_items():
    items = [
        {"title" : "Ryan Reynolds", "description" : "Deadpool"},
        {"title" : "Morena Baccarin", "description" : "Vanessa"}
    ]

    return items