from typing import Any, List, Optional
from framework.resources.base_resource import BaseResource
from app.models.recipe import RecipeSection
from app.services.service_factory import ServiceFactory
from datetime import datetime

class RecipeResource(BaseResource):

    def __init__(self, config):
        super().__init__(config)

        # TODO -- Replace with dependency injection.
        #
        self.data_service = ServiceFactory.get_service("RecipeResourceDataService")
        self.database = "recipe_management"
        self.collection = "Recipe"
        self.key_field = "recipe_id"


    def get_by_key(self, key: str) -> RecipeSection:
        d_service = self.data_service # get recipe data from db

        result = d_service.get_data_object(
            self.database, self.collection, key_field=self.key_field, key_value=key
        )

        result['create_time'] = str(result['create_time'])
        result = RecipeSection(**result) # store result as Recipe model
        return result

    def get_paginated(self, skip: int = 0, limit: int = 10, filter_by: Optional[str] = None) -> (
    List[RecipeSection], int):
        query_filter = {}
        if filter_by:
            query_filter["recipe_name"] = filter_by

        results = self.data_service.get_paginated_data(
            database_name=self.database,
            table_name=self.collection,
            offset=skip,
            limit=limit
        )

        total_count = self.data_service.get_total_count(
            database_name=self.database,
            table_name=self.collection,
            filters=query_filter
        )

        for result in results:
            if "create_time" in result and isinstance(result["create_time"], datetime):
                result["create_time"] = result["create_time"].strftime("%Y-%m-%d %H:%M:%S")

        return [RecipeSection(**result) for result in results], total_count

    def create_recipe(self, recipe_data: dict):
         d_service = self.data_service
         recipe_data.pop('links', None)
         new_recipe = d_service.create_data_object(
             self.database, self.collection, recipe_data
         )
         if not new_recipe:
             raise Exception("Failed to create new recipe")
         return RecipeSection(**new_recipe)

    def update_recipe(self, key: int, recipe_data: dict):
         d_service = self.data_service
         updated_recipe = d_service.update_data_object(
             self.database, self.collection, key_field=self.key_field, key_value=key, update_data=recipe_data
         )
         return RecipeSection(**updated_recipe)

    def delete_recipe(self, key: int) -> Any:
         d_service = self.data_service
         return d_service.delete_data_object(
             self.database, self.collection, key_field=self.key_field, key_value=key
         )
