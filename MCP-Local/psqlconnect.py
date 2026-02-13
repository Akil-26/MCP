import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    print("Connection to PostgreSQL database successful!")
    cursor = connection.cursor()
    cursor.execute("Select age from students")
    for row in cursor.fetchall():
        print(row)

    cursor.close()
    connection.close()

except Exception as e:
    print(f"An error occurred while connecting to the database: {e}")