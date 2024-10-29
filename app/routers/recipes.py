from fastapi import APIRouter, HTTPException
from app.models.recipe import RecipeSection
from app.models.ingredient import Ingredient
from app.models.instruction import Instruction
from app.resources.recipe_resource import RecipeResource
from app.services.service_factory import ServiceFactory

router = APIRouter()

# Composite GET for Recipe and Sub-Resources
@router.get("/recipes_sections/{recipe_id}", tags=["recipes"])
async def get_recipe(recipe_id: str) -> RecipeSection:
    recipe_service = ServiceFactory.get_service("RecipeResource")
    ingredient_service = ServiceFactory.get_service("IngredientResource")
    instruction_service = ServiceFactory.get_service("InstructionResource")

    # Fetch recipe
    recipe = recipe_service.get_by_key(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Fetch related sub-resources
    ingredients = ingredient_service.get_by_recipe_id(recipe_id)
    instructions = instruction_service.get_by_recipe_id(recipe_id)

    # Aggregate data into RecipeSection model
    recipe.ingredients = ingredients
    recipe.instructions = instructions

    return recipe

# Composite POST for creating a new Recipe with Sub-Resources
@router.post("/recipes_sections/", tags=["recipes"])
async def create_recipe(recipe_data: RecipeSection) -> RecipeSection:
    recipe_service = ServiceFactory.get_service("RecipeResource")
    ingredient_service = ServiceFactory.get_service("IngredientResource")
    instruction_service = ServiceFactory.get_service("InstructionResource")

    # Create main recipe entry
    new_recipe = recipe_service.create_recipe(recipe_data.dict(exclude={"ingredients", "instructions", "user_preferences"}))

    # Create sub-resources
    for ingredient in recipe_data.ingredients:
        ingredient_service.create_ingredient({"recipe_id": new_recipe.recipe_id, **ingredient.dict()})
    for instruction in recipe_data.instructions:
        instruction_service.create_instruction({"recipe_id": new_recipe.recipe_id, **instruction.dict()})

    return new_recipe

# Composite PUT for updating a Recipe and Sub-Resources
@router.put("/recipes_sections/{recipe_id}", tags=["recipes"])
async def update_recipe(recipe_id: str, recipe_data: RecipeSection) -> RecipeSection:
    recipe_service = ServiceFactory.get_service("RecipeResource")
    ingredient_service = ServiceFactory.get_service("IngredientResource")
    instruction_service = ServiceFactory.get_service("InstructionResource")

    # Update main recipe entry
    updated_recipe = recipe_service.update_recipe(recipe_id, recipe_data.dict(exclude={"ingredients", "instructions", "user_preferences"}))

    # Update sub-resources
    for ingredient in recipe_data.ingredients:
        ingredient_service.update_ingredient({"recipe_id": recipe_id, **ingredient.dict()})
    for instruction in recipe_data.instructions:
        instruction_service.update_instruction({"recipe_id": recipe_id, **instruction.dict()})

    return updated_recipe

# Composite DELETE for removing a Recipe and its Sub-Resources
@router.delete("/recipes_sections/{recipe_id}", tags=["recipes"])
async def delete_recipe(recipe_id: str):
    recipe_service = ServiceFactory.get_service("RecipeResource")
    ingredient_service = ServiceFactory.get_service("IngredientResource")
    instruction_service = ServiceFactory.get_service("InstructionResource")

    # Delete main recipe entry
    recipe_deleted = recipe_service.delete_recipe(recipe_id)
    if not recipe_deleted:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Delete associated sub-resources
    ingredient_service.delete_by_recipe_id(recipe_id)
    instruction_service.delete_by_recipe_id(recipe_id)

    return {"message": "Recipe and related sub-resources deleted successfully"}
