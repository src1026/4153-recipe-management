from typing import List, Dict, Any
from framework.resources.base_resource import BaseResource
from app.models.recipe import RecipeSection
from app.models.ingredient import Ingredient
from app.models.instruction import Instruction
from app.services.service_factory import ServiceFactory
from app.resources.ingredient_resource import IngredientResource
from app.resources.instruction_resource import InstructionResource

class RecipeResource(BaseResource):
    def __init__(self, config):
        super().__init__(config)
        self.data_service = ServiceFactory.get_service("RecipeResourceDataService")
        self.database = "recipe_management"
        self.collection = "Recipe"
        self.key_field = "recipe_id"

        # Initialize Ingredient and Instruction resources
        self.ingredient_resource = IngredientResource(config)
        self.instruction_resource = InstructionResource(config)

    def get_by_key(self, key: str) -> RecipeSection:
        # Retrieve recipe data
        recipe_data = self.data_service.get_data_object(
            self.database, self.collection, key_field=self.key_field, key_value=key
        )
        recipe_data['create_time'] = str(recipe_data['create_time'])
        
        # Retrieve ingredients and instructions related to the recipe
        ingredients = self.ingredient_resource.get_by_recipe_id(key)
        instructions = self.instruction_resource.get_by_recipe_id(key)
        
        # Build the RecipeSection including ingredients and instructions
        recipe_section = RecipeSection(**recipe_data)
        recipe_section.ingredients = ingredients
        recipe_section.instructions = instructions
        return recipe_section

    def create_recipe(self, recipe_data: dict, ingredients_data: List[Dict[str, Any]], instructions_data: List[Dict[str, Any]]) -> RecipeSection:
        # Create the recipe
        new_recipe = self.data_service.create_data_object(
            self.database, self.collection, recipe_data
        )
        recipe_id = new_recipe[self.key_field]

        # Create related ingredients and instructions
        ingredients = [self.ingredient_resource.create_ingredient({**ingredient, "recipe_id": recipe_id}) for ingredient in ingredients_data]
        instructions = [self.instruction_resource.create_instruction({**instruction, "recipe_id": recipe_id}) for instruction in instructions_data]
        
        # Return the full recipe with its sub-resources
        recipe_section = RecipeSection(**new_recipe)
        recipe_section.ingredients = ingredients
        recipe_section.instructions = instructions
        return recipe_section

    def update_recipe(self, key: str, recipe_data: dict, ingredients_data: List[Dict[str, Any]], instructions_data: List[Dict[str, Any]]) -> RecipeSection:
        # Update recipe core data
        updated_recipe = self.data_service.update_data_object(
            self.database, self.collection, key_field=self.key_field, key_value=key, update_data=recipe_data
        )
        
        # Update ingredients
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.pop("ingredient_id", None)
            if ingredient_id:
                self.ingredient_resource.update_ingredient(ingredient_id, ingredient_data)

        # Update instructions
        for instruction_data in instructions_data:
            instruction_id = instruction_data.pop("instruction_id", None)
            if instruction_id:
                self.instruction_resource.update_instruction(instruction_id, instruction_data)
        
        # Retrieve the complete updated recipe with ingredients and instructions
        recipe_section = RecipeSection(**updated_recipe)
        recipe_section.ingredients = self.ingredient_resource.get_by_recipe_id(key)
        recipe_section.instructions = self.instruction_resource.get_by_recipe_id(key)
        return recipe_section

    def delete_recipe(self, key: str) -> Any:
        # Delete recipe
        result = self.data_service.delete_data_object(
            self.database, self.collection, key_field=self.key_field, key_value=key
        )
        
        # Delete all related ingredients and instructions
        self.ingredient_resource.delete_by_recipe_id(key)
        self.instruction_resource.delete_by_recipe_id(key)
        
        return result
