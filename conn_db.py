import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    return connection


if __name__ == "__main__":

    try:
        conn = get_connection()

        print("✅ PostgreSQL connection successful")

        cursor = conn.cursor()

        cursor.execute("SELECT version();")

        version = cursor.fetchone()

        print("PostgreSQL Version:")
        print(version[0])

        cursor.close()
        conn.close()

        print("✅ Connection closed")

    except Exception as e:
        print("❌ PostgreSQL connection failed")
        print("Error:", e)