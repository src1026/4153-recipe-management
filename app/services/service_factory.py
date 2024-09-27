from framework.services.service_factory import BaseServiceFactory
import app.resources.recipe_resource as recipe_resource
# from framework.services.data_access.MySQLRDBDataService import MySQLRDBDataService
import boto3 # dynamo


# TODO -- Implement this class
class ServiceFactory(BaseServiceFactory):
    def __init__(self):
        super().__init__()

    @classmethod
    def get_service(cls, service_name):
        #
        # TODO -- The terrible, hardcoding and hacking continues.
        #
        if service_name == 'RecipeResource':
            result = recipe_resource.RecipeResource(config=None)
        elif service_name == 'RecipeResourceDataService':
            dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
            table = dynamodb.Table('Recipes')
            result = RecipeDynamoDBDataService(table)
        else:
            result = None

        return result