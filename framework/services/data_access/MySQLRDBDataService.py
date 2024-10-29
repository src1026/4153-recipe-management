import pymysql
from .BaseDataService import DataDataService
from pymysql import Error

class MySQLRDBDataService(DataDataService):
    """
    A generic data service for MySQL databases. The class implement common
    methods from BaseDataService and other methods for MySQL. More complex use cases
    can subclass, reuse methods and extend.
    """

    def __init__(self, context):
        super().__init__(context)

    def _get_connection(self):
        try: 
            self.connection = pymysql.connect(
                host=self.context["host"],
                port=self.context["port"],
                user=self.context["user"],
                passwd=self.context["password"],
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            if self.connection:
                print("Successfully connected to the database")
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1;")  # Simple query to test the connection
                print("Test query executed successfully")
            else:
                print("Connection failed!")
            return self.connection
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            self.connection = None

    def get_data_object(self,
                        database_name: str,
                        collection_name: str,
                        key_field: str,
                        key_value: str):
        """
        See base class for comments.
        """

        connection = None
        result = None

        try:
            sql_statement = f"SELECT * FROM {database_name}.{collection_name} " + \
                        f"where {key_field}=%s"
            connection = self._get_connection()
            cursor = connection.cursor()
            print("SQL = ", cursor.mogrify(sql_statement, [key_value]))
            cursor.execute(sql_statement, [key_value])
            result = cursor.fetchone()
        except Exception as e:
            if connection:
                connection.close()
            print("Something is wrong with your connection!")

        return result


    def get_paginated_data(self, database_name: str, table_name: str, offset: int = 0, limit: int = 10):
        connection = self._get_connection()

        results = []
        try:
            if not connection:
                raise Exception("No database connection!")

            sql_statement = f"SELECT * FROM {database_name}.{table_name} LIMIT %s OFFSET %s"
            connection = self._get_connection()
            if not connection:
                raise Exception("Connection failed.")
            with connection.cursor() as cursor:
                cursor.execute(sql_statement, [limit, offset])
                results = cursor.fetchall()
        except Exception as e:
            print(f"error with the paginated query: {e}")
        finally:
            if connection:
                connection.close()
                print("connection closed")
        return results
