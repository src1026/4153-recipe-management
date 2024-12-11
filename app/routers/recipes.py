from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.models.recipe import RecipeSection, PaginatedRecipeResponse
from app.resources.recipe_resource import RecipeResource
from app.services.service_factory import ServiceFactory
from typing import List, Optional

router = APIRouter()

def get_recipe_resource() -> RecipeResource:
    return RecipeResource(config={})


# QUESTION: It seems that we can only get by recipe_id but not recipe name?
@router.get("/recipe-section/{recipe_id}", tags=["recipes"], response_model=RecipeSection)
async def get_recipes(recipe_id: str):
    res = ServiceFactory.get_service("RecipeResource")
    print(recipe_id)
    result = res.get_by_key(recipe_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    if isinstance(result, dict):
        result = RecipeSection(**result)

    # HATEOAS
    result.links = [
        {"rel": "self", "href": f"/recipe-section/{recipe_id}", "method": "GET"},
        {"rel": "update", "href": f"/recipe-section/{recipe_id}", "method": "PUT"},
        {"rel": "delete", "href": f"/recipe-section/{recipe_id}", "method": "DELETE"},
        {"rel": "comments", "href": f"/recipe-section/{recipe_id}/comments", "method": "GET"},
    ]
    return result
    # TODO: Add error handling (currently getting errors for NoneTypes )
    # TODO: Do lifecycle management for singleton resource

@router.get("/recipe-section", tags=["recipes"], response_model=PaginatedRecipeResponse)
async def get_recipe(
    skip: int = Query(0, alias="offset"),
    limit: int = Query(10),
    filter_by: Optional[str] = None,
    recipe_resource: RecipeResource = Depends(get_recipe_resource)
):
    results, total_count = recipe_resource.get_paginated(skip=skip, limit=limit, filter_by=filter_by)
    if not results:
        raise HTTPException(status_code=404, detail="No recipes found!")

    # Add HATEOAS links to each recipe
    recipes_with_links = []
    for recipe in results:
        recipe_dict = recipe.model_dump()
        recipe_dict["links"] = [
            {"rel": "self", "href": f"/recipe-section/{recipe.recipe_id}", "method": "GET"},
            {"rel": "update", "href": f"/recipe-section/{recipe.recipe_id}", "method": "PUT"},
            {"rel": "delete", "href": f"/recipe-section/{recipe.recipe_id}", "method": "DELETE"},
        ]
        recipes_with_links.append(RecipeSection(**recipe_dict))

    return {
        "data": recipes_with_links,
        "pagination": {
            "offset": skip,
            "limit": limit,
            "total_count": total_count
        },
    }


@router.post("/recipe-section", tags=["recipes"], response_model=RecipeSection, status_code=status.HTTP_201_CREATED)
async def create_recipe(
        recipe_data: RecipeSection,
        recipe_resource: RecipeResource = Depends(get_recipe_resource)
):
    new_recipe = recipe_resource.create_recipe(recipe_data.dict())
    if not new_recipe:
        raise HTTPException(status_code=400, detail="Recipe creation failed")
    return new_recipe, {"Location": f"/recipe-section/{new_recipe.recipe_id}"}

@router.put("/recipe-section/{recipe_id}", tags=["recipes"], status_code=status.HTTP_202_ACCEPTED)
async def update_recipe(
    recipe_id: str,
    recipe_data: RecipeSection,
    recipe_resource: RecipeResource = Depends(get_recipe_resource)
):
    print("Before moving forward, let's validate recipa_data's data!")
    for k, v in recipe_data.dict().items():
        print(str(k) + "=" + str(v))
    updated_recipe = recipe_resource.update_recipe(recipe_id, recipe_data.dict())
    print("Program finished updating, let's check, is it None? " + str(update_recipe==None))
    if not updated_recipe:
        raise HTTPException(status_code=400, detail="Failed to update recipe")
    return updated_recipe


    # task_id = f"update-{recipe_id}"
    # status_url = f"/tasks/{task_id}/status"

    # return {
    #     "message": "Update accepted",
    #     "task_status_url": status_url
    # }

@router.delete("/recipe-section/{recipe_id}", tags=["recipes"])
async def delete_recipe(recipe_id: str, recipe_resource: RecipeResource = Depends(get_recipe_resource)):
    """
    Delete a recipe by ID.
    """
    success = recipe_resource.delete_recipe(recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found!")

    return {
        "message": "Recipe deleted successfully!",
        "links": [
            {"rel": "list", "href": "/recipe-section", "method": "GET"},
        ],
    }
