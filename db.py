import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_DSN = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DB_DSN)
