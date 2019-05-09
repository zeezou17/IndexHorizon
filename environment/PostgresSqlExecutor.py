import psycopg2
import configparser
import sys
from environment.Constants import Constants


class PostgresSqlExecutor:
    # attribute which will hold the postgres connection
    connection = None
    hypo_indexes_dict = dict()

    @staticmethod
    def __get_connection():
        # create connection only if it is not done before
        if PostgresSqlExecutor.connection is None:
            # connect to postgres
            try:
                # read database config from config file
                config = configparser.ConfigParser()
                config.read('../config.ini')
                database_config = dict(config.items('Database'))
                PostgresSqlExecutor.connection = psycopg2.connect(database=database_config["dbname"],

                                                                  user=database_config["user"],
                                                                  password=database_config["password"],
                                                                  host=database_config["host"],
                                                                  port=database_config["port"])
                PostgresSqlExecutor.connection.autocommit = True
            # capture connection exception
            except psycopg2.OperationalError as exception:
                print('Unable to connect to postgres \n Reason: {0}').format(str(exception))
                # exit code
                sys.exit(1)
            else:
                cursor = PostgresSqlExecutor.connection.cursor()
                # Print PostgreSQL version
                cursor.execute("SELECT version();")
                record = cursor.fetchone()
                print("***You are connected to below Postgres database*** \n ", record, "\n")
        return PostgresSqlExecutor.connection

    @staticmethod
    def execute_select_query(query):
        cursor = PostgresSqlExecutor.__get_connection().cursor()
        cursor.execute(query)
        returned_rows = cursor.fetchall()
        cursor.close()
        return returned_rows

    @staticmethod
    def execute_select_query_and_get_row_count(query):
        cursor = PostgresSqlExecutor.__get_connection().cursor()
        # remove all values before from and replace with select count(*) and remove order by clause if present
        query_to_execute = ' '.join(query.strip().replace('\n', ' ').lower().split())
        from_index = query_to_execute.find("from")
        to_index = query_to_execute.find("order by")
        query_to_execute = "Select count(*) " + query_to_execute[from_index:to_index]
        cursor.execute(query_to_execute)
        returned_count = cursor.fetchone()
        cursor.close()
        return returned_count

    @staticmethod
    def create_hypo_index(table_name, col_name):
        key = table_name + Constants.MULTI_KEY_CONCATENATION_STRING + col_name
        if key not in PostgresSqlExecutor.hypo_indexes_dict:
            cursor = PostgresSqlExecutor.__get_connection().cursor()
            cursor.execute(Constants.CREATE_HYPO_INDEX.format(table_name, col_name))
            returned_index_id = cursor.fetchone()
            cursor.close()
            PostgresSqlExecutor.hypo_indexes_dict[key] = returned_index_id[0]

    @staticmethod
    def remove_hypo_index(table_name, col_name):
        key = table_name + Constants.MULTI_KEY_CONCATENATION_STRING + col_name
        if key in PostgresSqlExecutor.hypo_indexes_dict:
            cursor = PostgresSqlExecutor.__get_connection().cursor()

            cursor.execute(Constants.REMOVE_HYPO_INDEX.format(PostgresSqlExecutor.hypo_indexes_dict.get(key, 0)))
            cursor.close()
            PostgresSqlExecutor.hypo_indexes_dict.pop(key, None)

    @staticmethod
    def remove_all_hypo_indexes():
        cursor = PostgresSqlExecutor.__get_connection().cursor()
        cursor.execute(Constants.REMOVE_ALL_HYPO_INDEXES)
        cursor.close()
