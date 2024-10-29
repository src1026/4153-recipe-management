from framework.services.service_factory import BaseServiceFactory
import app.resources.recipe_resource as recipe_resource
from framework.services.data_access.MySQLRDBDataService import MySQLRDBDataService


# TODO -- Implement this class
class ServiceFactory(BaseServiceFactory):
    def __init__(self):
        super().__init__()


    @classmethod
    def get_service(self, service_name):
        #
        # TODO -- The terrible, hardcoding and hacking continues.
        #
        if service_name == 'RecipeResource':
            result = recipe_resource.RecipeResource(config=None)
        elif service_name == 'RecipeResourceDataService':
            print("inside get_service")
            context = dict(user="jigglypuff7", password="Jigglypuff7!",
                            host="jigglypuff7.c7s86kaawl6v.us-east-2.rds.amazonaws.com", port=3306)
            print("initialized context.")
            data_service = MySQLRDBDataService(context=context)
            print(data_service)
            result = data_service
            """
            context = dict(user="root", password="dbuserdbuser",
                           host="localhost", port=3306)
            """
        else:
            print("No such service name")
            result = None

        return result