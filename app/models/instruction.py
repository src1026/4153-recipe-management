from typing import Optional
from pydantic import BaseModel

class Instruction(BaseModel):
    instruction_id: Optional[int] = None  # Unique ID for the instruction
    recipe_id: Optional[int] = None  # FK to a Recipe
    step_number: Optional[int] = None  # Step number in the sequence
    description: Optional[str] = None  # Detailed instruction text

    class Config:
        json_schema_extra = {
            "example": {
                "instruction_id": 1,
                "recipe_id": 123,
                "step_number": 1,
                "description": "Boil water in a large pot."
            }
        }
