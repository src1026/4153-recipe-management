from typing import Optional
from pydantic import BaseModel

class Ingredient(BaseModel):
    ingredient_id: Optional[int] = None  # Unique ID for the ingredient
    recipe_id: Optional[int] = None  # FK to a Recipe
    name: Optional[str] = None  # Ingredient name (e.g., "Tomato")
    quantity: Optional[str] = None  # Quantity (e.g., "2 cups")
    unit: Optional[str] = None  # Unit of measurement (e.g., "grams")

    class Config:
        json_schema_extra = {
            "example": {
                "ingredient_id": 1,
                "recipe_id": 123,
                "name": "Tomato",
                "quantity": "2",
                "unit": "cups"
            }
        }
