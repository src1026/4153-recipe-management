from fastapi.testclient import TestClient
from app.main import app  # Ensure this imports the actual FastAPI app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FastAPI App"}
