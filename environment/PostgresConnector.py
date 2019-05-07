import psycopg2
import configparser
import sys


class PostgresConnector:
    # attribute which will hold the postgres connection
    connection = None

    @staticmethod
    def get_connection():
        # create connection only if it is not done before
        if PostgresConnector.connection is None:
            # connect to postgres
            try:
                # read database config from config file
                config = configparser.ConfigParser()
                config.read('../config.ini')
                database_config = dict(config.items('Database'))
                PostgresConnector.connection = psycopg2.connect(database=database_config["dbname"],
                                                                user=database_config["user"],
                                                                password=database_config["password"],
                                                                host=database_config["host"],
                                                                port=database_config["port"])
            # capture connection exception
            except psycopg2.OperationalError as exception:
                print('Unable to connect to postgres \n Reason: {0}').format(str(exception))
                # exit code
                sys.exit(1)
            else:
                cursor = PostgresConnector.connection.cursor()
                # Print PostgreSQL version
                cursor.execute("SELECT version();")
                record = cursor.fetchone()
                print("***You are connected to below Postgres database*** \n ", record, "\n")
        return PostgresConnector.connection
