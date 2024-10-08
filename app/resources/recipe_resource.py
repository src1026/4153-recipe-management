from typing import Any
from framework.resources.base_resource import BaseResource
from app.models.recipe import RecipeSection
from app.services.service_factory import ServiceFactory

class RecipeResource(BaseResource):

    def __init__(self, config):
        super().__init__(config)

        # TODO -- Replace with dependency injection.
        #
        self.data_service = ServiceFactory.get_service("RecipeResourceDataService")
        self.database = "recipe_management"
        self.collection = "recipe_sections"
        self.key_field = "recipe_name"

    def get_by_key(self, key: str) -> RecipeSection:
        d_service = self.data_service # get recipe data from db

        result = d_service.get_data_object(
            self.database, self.collection, key_field=self.key_field, key_value=key
        )

        result = RecipeSection(**result) # store result as Recipe model
        return result


    # def create_recipe(self, recipe_data: dict) -> Recipe:
    #     d_service = self.data_service

    #     new_recipe = d_service.create_data_object(
    #         self.database, self.collection, recipe_data
    #     )
    #     return Recipe(**new_recipe)

    # def update_recipe(self, key: int, recipe_data: dict) -> Recipe:
    #     d_service = self.data_service
    #     updated_recipe = d_service.update_data_object(
    #         self.database, self.collection, key_field=self.key_field, key_value=key, update_data=recipe_data
    #     )
    #     return Recipe(**updated_recipe)

    # def delete_recipe(self, key: int) -> Any:
    #     d_service = self.data_service
    #     return d_service.delete_data_object(
    #         self.database, self.collection, key_field=self.key_field, key_value=key
    #     )
