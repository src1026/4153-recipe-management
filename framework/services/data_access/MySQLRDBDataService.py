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
        if not connection:
            print("No connection")
            raise Exception("Failed to establish a database connection.")

        if not data:
            print("No data provided for insertion")
            raise ValueError("Data dictionary is empty.")

        try:
            print("Testing connection and cursor creation...")
            cursor = connection.cursor()
            print("Cursor created successfully.")

            # To see databse content for debugging purpose
            print("Existing entries in recipe database:")
            with connection.cursor() as cursor:
                # Replace 'your_table' with the actual table name
                cursor.execute(f"SELECT * FROM `{database_name}`.`{collection_name}`")
                
                # Step 3: Fetch and print the results
                rows = cursor.fetchall()
                
                if rows:
                    print("Existing records in the table:")
                    for row in rows:
                        print(row)  # Print each row as a dictionary
                else:
                    print("The table is empty.")
            # QUESTION: cuisine_id limited options? e.g. when I set cuisine_id:4, it gives the error message MySQL Error: (1452, 'Cannot add or update a child row: a foreign key constraint fails (`recipe_management`.`Recipe`, CONSTRAINT `Recipe_ibfk_2` FOREIGN KEY (`cuisine_id`) REFERENCES `Cuisine` (`cuisine_id`))')
            # Does this mean we need to manage the table containing cuisine_id as well (AKA not only updating recipe table?)

            # Remove recipe_id if it's None
            data = {k: v for k, v in data.items() if v is not None}

            # Prepare SQL
            columns = ', '.join([f"`{col}`" for col in data.keys()])  # Handle column names
            placeholders = ', '.join(['%s'] * len(data))  # Generate placeholders
            sql_statement = f"INSERT INTO `{database_name}`.`{collection_name}` ({columns}) VALUES ({placeholders})"

            print("SQL Statement:", sql_statement)
            print("Data Values:", list(data.values()))

            # Execute SQL
            with connection.cursor() as cursor:
                print(list(data.values()))
                print("---------------------------")
                cursor.execute(sql_statement, list(data.values()))
                connection.commit()
                new_id = cursor.lastrowid  # Fetch the auto-incremented primary key
                data['recipe_id'] = new_id
                print("Inserted data:", data)
                return data

        except pymysql.MySQLError as e:
            print(f"MySQL Error: {e}")
            return None
        except Exception as e:
            print(f"General Error inserting data: {e}")
            return None
        finally:
            if connection:
                connection.close()
                print("Database connection closed.")

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
                total_count = result["total"] if result else 0 # Question: Where did the "total" column come from?
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
    
    def update_data_object(self, database_name: str, collection_name: str, data: dict):
        for k, v in data.items():
            print(str(k) + "=" + str(v))
        connection = self._get_connection()
        if not connection:
            print("No connection")
            raise Exception("Failed to establish a database connection.")

        if not data:
            print("No data provided for insertion")
            raise ValueError("Data dictionary is empty.")
        
        try:
            print("Testing connection and cursor creation...")
            cursor = connection.cursor()
            print("Cursor created successfully.")
            
            key = data.get('recipe_id')
            if not key:
                print("Missing 'recipe_id' in data.")
                raise ValueError("recipe_id is required for update.")
            
            # Prepare SQL
            columns = ', '.join([f"`{col}` = %s" for col in data.keys()])  # Handle column names with placeholders
            sql_statement = f"UPDATE `{database_name}`.`{collection_name}` SET {columns} WHERE `recipe_id` = %s"
            
            print("SQL Statement:", sql_statement)
            print("Data Values:", list(data.values()))

            # Execute the query with the parameters
            cursor.execute(sql_statement, list(data.values()) + [key])

            # Commit the changes
            connection.commit()
            print("Update successful.")
        
            # Check if data is None before passing it to another function
            if data is None:
                print("Data is None, returning None.")
                return None
            return data
        except pymysql.MySQLError as e:
            print(f"MySQL Error: {e}")
            return None
        except Exception as e:
            print(f"General Error inserting data: {e}")
            return None
        finally:
            if connection:
                connection.close()
                print("Database connection closed.")

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
