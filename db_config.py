import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MySQL_0905"),
        database=os.getenv("pasabuy_db")
    )