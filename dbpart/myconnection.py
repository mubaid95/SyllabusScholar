import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

load_dotenv()
def connect():
    try:
        db_config = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT')
        }
        conn = psycopg2.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None
