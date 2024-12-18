from fastapi import APIRouter, Depends, Query, HTTPException, status, Request, FastAPI, UploadFile
from app.models.recipe import RecipeSection, PaginatedRecipeResponse
from app.resources.recipe_resource import RecipeResource
from app.services.service_factory import ServiceFactory
from typing import List, Optional
from opentelemetry import trace
import logging, uuid
import datetime
from app.services.gcs_service import upload_image
import os 

router = APIRouter()
app = FastAPI(
    title="Recipe Management API",
    description="API for managing and retrieving recipes"
)

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

@router.get("/recipes_sections/{recipe_id}", 
            tags=["recipes"], 
            response_model=RecipeSection, 
            summary="get a specific recipe", 
            description="retreive a recipe by it's unique ID based on key words",
            responses={
                200: {
                    "description": "Recipe found successfully",
                    "model": RecipeSection,  # Model used in the response
                    "example": {
                        "recipe_id": 123,
                        "recipe_name": "Spaghetti Carbonara",
                        "content": "A delicious Italian pasta dish",
                        "rating": 4.5,
                        "cuisine_id": 1,
                        "ingredient_id": ["spaghetti", "eggs", "bacon"],
                        "cooking_time": 20,
                        "create_time": "2024-12-15T12:00:00"
                    }
                },
                404: {
                    "description": "Recipe not found"
                }
            })
            
async def get_recipes(recipe_id: str):
    res = ServiceFactory.get_service("RecipeResource")
    result = res.get_by_key(recipe_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    if isinstance(result, dict):
        result = RecipeSection(**result)

    if result.pictures:
        bucket_url = f"https://storage.googleapis.com/jigglypuff-images/"
        result.pictures = bucket_url + result.pictures

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

@router.get("/recipes_sections", 
            tags=["recipes"], 
            response_model=PaginatedRecipeResponse, 
            summary="list recipes", 
            description="retreive a paginated list of recipes with optional filtering",
            responses={200: {
                "description": "A list of recipes",
                "model": PaginatedRecipeResponse,
                "example": {
                    "data": [
                        {
                            "recipe_id": 123,
                            "recipe_name": "Pasta",
                            "content": "Boil pasta, cook sauce, mix ingredients together.",
                            "rating": 4.5,
                            "cuisine_id": 2,
                            "ingredient_id": "1, 2, 3",
                            "comment": "101, 102",
                            "cooking_time": 30,
                            "create_time": "2024-09-27T09:54:51Z",
                            "pictures": "img1",
                            "links": [
                                {"rel": "self", "href": "/recipes_sections/123", "method": "GET"},
                                {"rel": "update", "href": "/recipes_sections/123", "method": "PUT"},
                                {"rel": "delete", "href": "/recipes_sections/123", "method": "DELETE"},
                                {"rel": "comments", "href": "/recipes_sections/123/comments", "method": "GET"}
                            ]
                        }
                    ],
                    "pagination": {
                        "offset": 0,
                        "limit": 100,
                        "total_count": 1
                    }
                }
            }})

async def get_recipe(
    skip: int = Query(0, alias="offset"),
    limit: int = Query(100),
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


@router.post("/recipes_sections", 
            tags=["recipes"], 
            response_model=RecipeSection, 
            status_code=status.HTTP_201_CREATED, 
            summary="create new recipe", 
            description="create a new recipe with unique ID using required information",
            responses={201: {"model": RecipeSection, "example": {
                "recipe_id": 123,
                "recipe_name": "Pasta",
                "content": "Boil pasta, cook sauce, mix ingredients together.",
                "rating": 4.5,
                "cuisine_id": 2,
                "ingredient_id": "1, 2, 3",
                "comment": "101, 102",
                "cooking_time": 30,
                "create_time": "2024-09-27T09:54:51Z",
            }}}
)
async def create_recipe(
        recipe_data: RecipeSection,
        recipe_resource: RecipeResource = Depends(get_recipe_resource)
):
   
    """
    Create a new recipe.

    - **recipe_data**: The body of the request should contain the recipe information (e.g., name, ingredients, etc.).

    Example request body:
    ```json
    {
        "recipe_name": "Spaghetti Carbonara",
        "content": "A delicious Italian pasta dish",
        "rating": 4.5,
        "cuisine_id": 2,
        "ingredient_id": "1, 2, 3",
        "comment": "101, 102",
        "cooking_time": 30,
    }
    ```

    Example response:
    ```json
    {
        "recipe_id": 123,
        "recipe_name": "Spaghetti Carbonara",
        "content": "A delicious Italian pasta dish",
        "rating": 4.5,
        "cuisine_id": 1,
        "ingredient_id": ["spaghetti", "eggs", "bacon"],
        "cooking_time": 20,
        "create_time": "2024-12-15T12:00:00"
    }
    ```

    Responses:
    - **201 Created**: The recipe is created successfully.
    - **400 Bad Request**: Invalid input data.
    """

    recipe_data_dict = recipe_data.dict()
    recipe_data_dict.update({
        "recipe_id": await recipe_resource.get_next_recipe_id(),  
        "user_id": 5,
        "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    new_recipe = recipe_resource.create_recipe(recipe_data_dict)
    if not new_recipe:
        raise HTTPException(status_code=400, detail="Recipe creation failed")
    return new_recipe, {"Location": f"/recipes_sections/{new_recipe.recipe_id}"}

@router.put("/recipes_sections/{recipe_id}", tags=["recipes"], status_code=status.HTTP_202_ACCEPTED, summary="update existing recipe", description="update information in existing recipe")
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

@router.delete("/recipes_sections/{recipe_id}", 
               tags=["recipes"], 
               summary="delete existing recipe", 
               description="find and delete a recipe by it's unique ID",
               responses={200: {"description": "Recipe deleted successfully!"}})
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

@router.post("/upload")
async def upload_file(image: UploadFile):
    try:
        temp_path = os.path.join("/tmp", image.filename)
        with open(temp_path, "wb") as temp_file:
            content = await image.read()
            temp_file.write(content)

        public_url = upload_image(temp_path)

        os.remove(temp_path)

        return {"message": "Image uploaded successfully", "url": public_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {e}")
