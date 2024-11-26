from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.models.recipe import RecipeSection
from app.resources.recipe_resource import RecipeResource
from app.services.service_factory import ServiceFactory
from typing import List, Optional

router = APIRouter()

def get_recipe_resource() -> RecipeResource:
    return RecipeResource(config={})

@router.get("/recipes_sections/{recipe_id}", tags=["recipes"], response_model=RecipeSection)
async def get_recipes(recipe_id: str):
    res = ServiceFactory.get_service("RecipeResource")
    result = res.get_by_key(recipe_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    if isinstance(result, dict):
        result = RecipeSection(**result)

    # HATEOAS
    result.links = [
        {"rel": "self", "href": f"/recipes_sections/{recipe_id}", "method": "GET"},
        {"rel": "update", "href": f"/recipes_sections/{recipe_id}", "method": "PUT"},
        {"rel": "delete", "href": f"/recipes_sections/{recipe_id}", "method": "DELETE"},
        {"rel": "comments", "href": f"/recipes_sections/{recipe_id}/comments", "method": "GET"},
    ]
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

    # add hateoas links to each recipe
    recipes_with_links = [
        {
            **recipe.model_dump(),
            "links": [
                {"rel": "self", "href": f"/recipes_sections/{recipe.recipe_id}", "method": "GET"},
                {"rel": "update", "href": f"/recipes_sections/{recipe.recipe_id}", "method": "PUT"},
                {"rel": "delete", "href": f"/recipes_sections/{recipe.recipe_id}", "method": "DELETE"},
            ],
        }
        for recipe in results
    ]

    return {
        "data": recipes_with_links,
        "pagination": {
            "offset": skip,
            "limit": limit,
            "total_count": recipe_resource.get_total_count(filter_by=filter_by),
        },
    }

@router.post("/recipes_sections", tags=["recipes"], response_model=RecipeSection, status_code=status.HTTP_201_CREATED)
async def create_recipe(
        recipe_data: RecipeSection,
        recipe_resource: RecipeResource = Depends(get_recipe_resource)
):
    new_recipe = recipe_resource.create_recipe(recipe_data.dict())
    if not new_recipe:
        raise HTTPException(status_code=400, detail="Recipe creation failed")
    return new_recipe, {"Location": f"/recipes_sections/{new_recipe.recipe_id}"}

@router.put("/recipes_sections/{recipe_id}", tags=["recipes"], status_code=status.HTTP_202_ACCEPTED)
async def update_recipe(
    recipe_id: str,
    recipe_data: RecipeSection,
    recipe_resource: RecipeResource = Depends(get_recipe_resource)
):

    task_id = f"update-{recipe_id}"
    status_url = f"/tasks/{task_id}/status"

    return {
        "message": "Update accepted",
        "task_status_url": status_url
    }

@router.delete("/recipes_sections/{recipe_id}", tags=["recipes"])
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
            {"rel": "list", "href": "/recipes_sections", "method": "GET"},
        ],
    }
