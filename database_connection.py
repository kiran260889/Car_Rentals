import psycopg2
from configparser import ConfigParser

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        config = ConfigParser()
        config.read("config.ini")
        self.conn = psycopg2.connect(
            host=config["DATABASE"]["DB_HOST"],
            database=config["DATABASE"]["DB_NAME"],
            user=config["DATABASE"]["DB_USER"],
            password=config["DATABASE"]["DB_PASSWORD"],
            port=config["DATABASE"]["DB_PORT"]
        )

    def get_connection(self):
        return self.conn