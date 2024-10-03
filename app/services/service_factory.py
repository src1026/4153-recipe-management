from framework.services.service_factory import BaseServiceFactory
import app.resources.recipe_resource as recipe_resource
from framework.services.data_access.MySQLRDBDataService import MySQLRDBDataService


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
            # context = dict(user="jigglypuff", password="Jigglypuff7!",
            #                host="jigglypuff.cl8u62goqlob.us-east-2.rds.amazonaws.com", port=3306)
            context = dict(user="root", password="dbuserdbuser",
                           host="localhost", port=3306)
            data_service = MySQLRDBDataService(context=context)
            result = data_service
        else:
            result = None

        return result