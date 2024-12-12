from fastapi import APIRouter, Depends, Query, HTTPException, status, Request, FastAPI
from app.models.recipe import RecipeSection, PaginatedRecipeResponse
from app.resources.recipe_resource import RecipeResource
from app.services.service_factory import ServiceFactory
from typing import List, Optional
from opentelemetry import trace
import logging, uuid
router = APIRouter()
app = FastAPI()

# Middleware to handle correlation ID and logging
@app.middleware("http")
async def add_correlation_id_and_logging(request: Request, call_next):
    # Extract correlation ID from request headers
    correlation_id = request.headers.get("X-Trace-Id", None)
    if not correlation_id:
        correlation_id = generate_correlation_id()
        request.state.correlation_id = correlation_id

    # Log the incoming request
    logging.info(f"Incoming request: {request.method} {request.url} - Correlation ID: {correlation_id}")

    # Process the request
    with trace.get_tracer(__name__).start_as_current_span(f"{request.method} {request.url}", attributes={"correlation_id": correlation_id}):
        response = await call_next(request)

    # Log the outgoing response
    logging.info(f"Outgoing response: {response.status_code} - Correlation ID: {correlation_id}")

    return response

def generate_correlation_id() -> str:
    # Implementation to generate a unique correlation ID
    return str(uuid.uuid4())

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

@router.get("/recipes_sections", tags=["recipes"], response_model=PaginatedRecipeResponse)
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
            {"rel": "self", "href": f"/recipes_sections/{recipe.recipe_id}", "method": "GET"},
            {"rel": "update", "href": f"/recipes_sections/{recipe.recipe_id}", "method": "PUT"},
            {"rel": "delete", "href": f"/recipes_sections/{recipe.recipe_id}", "method": "DELETE"},
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
