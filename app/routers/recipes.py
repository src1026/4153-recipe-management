from fastapi import APIRouter
from app.models.recipe import RecipeSection
from app.resources.recipe_resource import RecipeResource
from app.services.service_factory import ServiceFactory

router = APIRouter()

@router.get("/recipes_sections/{recipe_id}", tags=["users"])
async def get_recipes(recipe_id: str) -> RecipeSection:
    res = ServiceFactory.get_service("RecipeResource")
    result = res.get_by_key(recipe_id)
    return result
    # TODO: Do lifecycle management for singleton resource

# @router.put("/recipe_section/{recipe_id}", tags=["recipes"])
# async def update_recipe(recipe_id: int, recipe_data: Recipe) -> Recipe:
#     res = ServiceFactory.get_service("RecipeResource")
#     result = res.update_recipe(recipe_id, recipe_data.dict())
#     return result

# @router.delete("/recipe_section/{recipe_id}", tags=["recipes"])
# async def delete_recipe(recipe_id: int):
#     res = ServiceFactory.get_service("RecipeResource")
#     result = res.delete_recipe(recipe_id)
#     if result:
#         return {"message" : "Recipe deleted!"}
#     else:
#         return {"message" : "Recipe's not found."}