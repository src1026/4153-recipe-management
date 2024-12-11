from fastapi.testclient import TestClient
from app.main import app  # Import the FastAPI app

client = TestClient(app)

def test_get_recipes_section():
    # Test retrieving a recipe section by ID
    recipe_id = "1"
    response = client.get(f"/recipes_sections/{recipe_id}")
    assert response.status_code in {200, 404}  # 404 if the recipe does not exist

def test_create_recipe():
    # Test creating a recipe
    recipe_data = {
        "recipe_id": 123,
        "recipe_name": "Pasta",
        "user_id": 1,
        "content": "Boil pasta, cook sauce, mix ingredients together.",
        "rating": 4.5,
        "cuisine_id": 2,
        "ingredient_id": "1, 2, 3",
        "comment": "Delicious!",
        "cooking_time": 30,
        "create_time": "2024-09-27T09:54:51Z",
        "pictures": "img1",
    }
    response = client.post("/recipes_sections", json=recipe_data)
    assert response.status_code == 201
    assert response.json()["recipe_name"] == "Pasta"

def test_update_recipe():
    # Test updating a recipe
    recipe_id = "123"
    updated_data = {
        "recipe_name": "Updated Pasta",
        "user_id": 1,
        "content": "Updated content",
        "rating": 4.8,
        "cuisine_id": 2,
        "ingredient_id": "1,2,3",
        "comment": "Updated comments",
        "cooking_time": 35,
        "create_time": "2024-09-30T12:00:00Z",
        "pictures": "img2"
    }
    response = client.put(f"/recipes_sections/{recipe_id}", json=updated_data)
    assert response.status_code == 202

def test_get_paginated_recipes():
    # Test getting a paginated list of recipes
    response = client.get("/recipes_sections?offset=0&limit=5")
    assert response.status_code == 200
    assert isinstance(response.json().get('data'), list)
