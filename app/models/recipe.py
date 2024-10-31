from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, HttpUrl

class RecipeSection(BaseModel):
    recipe_id: Optional[int] = None
    recipe_name: Optional[str] = None
    user_id: Optional[int] = None  # FK to a User
    content: Optional[str] = None
    rating: Optional[float] = None
    cuisine_id: Optional[int] = None  # FK to Cuisine
    # ingredient_id: Optional[List[int]] = None  # List of ingredient FK
    ingredient_id: Optional[str] = None  # List of ingredient FK
    # comment: Optional[List[int]] = None  # List of comment FK
    comment: Optional[str] = None
    cooking_time: Optional[int] = None
    create_time: Optional[str] = None
    # pictures: Optional[List[HttpUrl]] = None  # List of URLs to pictures
    pictures: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "recipe_id": 123,
                "recipe_name": "Pasta",
                "user_id": 1,
                "content": "Boil pasta, cook sauce, mix ingredients together.",
                "rating": 4.5,
                "cuisine_id": 2,
                "ingredient_id": "1, 2, 3",
                "comment": "101, 102",
                "cooking_time": 30,
                "create_time": "2024-09-27T09:54:51Z",
                "pictures": "img1" 
            }
        }