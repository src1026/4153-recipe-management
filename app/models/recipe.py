from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, HttpUrl

class Recipe(BaseModel):
    recipe_id: Optional[int] = None
    owner_id: Optional[int] = None  # FK to a User
    content: Optional[str] = None
    rating: Optional[float] = None
    cuisine_id: Optional[int] = None  # FK to Cuisine
    ingredient_id: Optional[List[int]] = None  # List of ingredient FK
    comment: Optional[List[int]] = None  # List of comment FK
    cooking_time: Optional[int] = None
    create_time: Optional[str] = None
    pictures: Optional[List[HttpUrl]] = None  # List of URLs to pictures

    class Config:
        json_schema_extra = {
            "example": {
                "recipe_id": 123,
                "owner_id": 1,
                "content": "Boil pasta, cook sauce, mix ingredients together.",
                "rating": 4.5,
                "cuisine_id": 2,
                "ingredient_id": [1, 2, 3],
                "comment": [101, 102],
                "cooking_time": 30,
                "create_time": "2024-09-27T09:54:51Z",
                "pictures": [
                    "https://example.com/images/recipe1.jpg",
                    "https://example.com/images/recipe2.jpg"
                ]
            }
        }