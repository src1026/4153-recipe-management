from fastapi import APIRouter, Depends, Query, HTTPException
from app.models.recipe import RecipeSection
from app.resources.recipe_resource import RecipeResource
from app.services.service_factory import ServiceFactory
from typing import List, Optional

router = APIRouter()

def get_recipe_resource() -> RecipeResource:
    return RecipeResource(config={})

@router.get("/recipes_sections/{recipe_id}", tags=["recipes"], response_model=RecipeSection)
async def get_recipes(recipe_id: str) -> RecipeSection:
    res = ServiceFactory.get_service("RecipeResource")
    result = res.get_by_key(recipe_id)
    return result
    # TODO: Add error handling (currently getting errors for NoneTypes )
    # TODO: Do lifecycle management for singleton resource


@router.get("/recipes_sections", tags=["recipes"], response_model=List[RecipeSection])
async def get_recipe(
        skip: int = Query(0, alias="offset"),
        limit: int = Query(10),
        filter_by: Optional[str] = None,
        recipe_resource: RecipeResource = Depends(get_recipe_resource)
):
    results = recipe_resource.get_paginated(skip=skip, limit=limit, filter_by=filter_by)
    if not results:
        raise HTTPException(status_code=404, detail="No recipes found!")
    return results

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