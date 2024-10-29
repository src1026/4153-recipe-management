from typing import List, Dict
from framework.resources.base_resource import BaseResource
from app.models.instruction import Instruction
from app.services.service_factory import ServiceFactory

class InstructionResource(BaseResource):

    def __init__(self, config):
        super().__init__(config)
        self.data_service = ServiceFactory.get_service("InstructionDataService")
        self.database = "recipe_management"
        self.collection = "Instruction"
        self.key_field = "instruction_id"

    def get_by_recipe_id(self, recipe_id: str) -> List[Instruction]:
        """Fetch instructions by recipe_id."""
        instructions = self.data_service.get_data_objects(
            self.database, self.collection, query={"recipe_id": recipe_id}
        )
        return [Instruction(**instruction) for instruction in instructions]

    def create_instruction(self, instruction_data: Dict) -> Instruction:
        """Create a new instruction for a recipe."""
        new_instruction = self.data_service.create_data_object(
            self.database, self.collection, instruction_data
        )
        return Instruction(**new_instruction)

    def update_instruction(self, instruction_data: Dict) -> Instruction:
        """Update an existing instruction."""
        updated_instruction = self.data_service.update_data_object(
            self.database, self.collection, query={"instruction_id": instruction_data["instruction_id"]}, update_data=instruction_data
        )
        return Instruction(**updated_instruction)

    def delete_by_recipe_id(self, recipe_id: str) -> bool:
        """Delete all instructions for a recipe."""
        return self.data_service.delete_data_objects(
            self.database, self.collection, query={"recipe_id": recipe_id}
        )
