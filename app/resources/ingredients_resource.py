from typing import List, Dict
from framework.resources.base_resource import BaseResource
from app.models.ingredient import Ingredient
from app.services.service_factory import ServiceFactory

class IngredientResource(BaseResource):

    def __init__(self, config):
        super().__init__(config)
        self.data_service = ServiceFactory.get_service("IngredientDataService")
        self.database = "recipe_management"
        self.collection = "Ingredient"
        self.key_field = "ingredient_id"

    def get_by_recipe_id(self, recipe_id: str) -> List[Ingredient]:
        """Fetch ingredients by recipe_id."""
        ingredients = self.data_service.get_data_objects(
            self.database, self.collection, query={"recipe_id": recipe_id}
        )
        return [Ingredient(**ingredient) for ingredient in ingredients]

    def create_ingredient(self, ingredient_data: Dict) -> Ingredient:
        """Create a new ingredient for a recipe."""
        new_ingredient = self.data_service.create_data_object(
            self.database, self.collection, ingredient_data
        )
        return Ingredient(**new_ingredient)

    def update_ingredient(self, ingredient_data: Dict) -> Ingredient:
        """Update an existing ingredient."""
        updated_ingredient = self.data_service.update_data_object(
            self.database, self.collection, query={"ingredient_id": ingredient_data["ingredient_id"]}, update_data=ingredient_data
        )
        return Ingredient(**updated_ingredient)

    def delete_by_recipe_id(self, recipe_id: str) -> bool:
        """Delete all ingredients for a recipe."""
        return self.data_service.delete_data_objects(
            self.database, self.collection, query={"recipe_id": recipe_id}
        )
