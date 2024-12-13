import pymysql
from .BaseDataService import DataDataService
from pymysql import Error
from typing import Optional, Any

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

    def create_data_object(self, database_name: str, collection_name: str, data: dict):
        connection = self._get_connection()
        try:
            if not connection:
                raise Exception("Failed to establish a database connection.")

            # Remove 'recipe_id' if present in the payload
            data.pop('recipe_id', None)

            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            sql_statement = f"INSERT INTO `{database_name}`.`{collection_name}` ({columns}) VALUES ({placeholders})"

            with connection.cursor() as cursor:
                cursor.execute(sql_statement, list(data.values()))
                connection.commit()
                new_id = cursor.lastrowid  # Retrieve the auto-generated ID
                data['recipe_id'] = new_id
                return data
        except pymysql.MySQLError as e:
            print(f"MySQL Error: {e}")
            return None
        finally:
            if connection:
                connection.close()

    def get_total_count(self, database_name: str, table_name: str, filters: Optional[dict] = None) -> int:
        """
        Get the total count of rows in the table, optionally applying filters.
        """
        connection = self._get_connection()
        if not connection:
            raise Exception("Failed to establish a database connection.")

        total_count = 0
        try:
            # base
            sql_statement = f"SELECT COUNT(*) AS total FROM {database_name}.{table_name}"

            # add filtering conditions if filters are provided
            if filters:
                conditions = " AND ".join([f"{key}=%s" for key in filters.keys()])
                sql_statement += f" WHERE {conditions}"

            # prepare parameters
            params = list(filters.values()) if filters else []

            # execute query
            with connection.cursor() as cursor:
                cursor.execute(sql_statement, params)
                result = cursor.fetchone()
                total_count = result["total"] if result else 0
        except Exception as e:
            print(f"Error fetching total count: {e}")
        finally:
            if connection:
                connection.close()
                print("Connection closed.")
        return total_count

    def get_paginated_data(self, database_name: str, table_name: str, offset: int = 0, limit: int = 10, filters: Optional[dict] = None):
        connection = self._get_connection()
        if not connection:
            raise Exception("Failed to establish a database connection.")
        results = []
        try:
            sql_statement = f"SELECT * FROM {database_name}.{table_name}"
            params = []
            if filters:
                conditions = " AND ".join([f"{key}=%s" for key in filters.keys()])
                sql_statement += f"WHERE {conditions}"
                params.extend(filters.values())

            sql_statement += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

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

    def delete_data_object(self, database_name: str, table_name: str, key_field: str, key_value: Any) -> bool:
        connection = self._get_connection()
        if not connection:
            raise Exception("Failed to establish a database connection.")

        try:
            sql_statement = f"DELETE FROM {database_name}.{table_name} WHERE {key_field}=%s"
            with connection.cursor() as cursor:
                cursor.execute(sql_statement, [key_value])
                connection.commit()
                return cursor.rowcount > 0  # returns True if a row was deleted
        except Exception as e:
            print(f"Error deleting data: {e}")
            return False
        finally:
            if connection:
                connection.close()
                print("Connection closed.")
