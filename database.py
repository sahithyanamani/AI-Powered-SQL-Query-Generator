import os
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging 
logging.basicConfig(level=logging.DEBUG)

# Database credentials
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")

# Create MySQL connection URL
DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

#create SQLAlchemy engine
try:
    logging.debug(f"Connecting to MySQL at {MYSQL_HOST}:{MYSQL_PORT}")
    engine= create_engine(DATABASE_URL, echo=True)
    logging.debug("Database connection successful!")
except Exception as e:
    logging.error(f"Database connection failed: {str(e)}")
    exit()
 
'''   
#Function to list databases
def list_databases():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SHOW DATABASES;")).fetchall()
            return {"databases": [row[0] for row in result]}
    except Exception as e:
        return {"error": str(e)}
    
#Function to list tables
def list_tables(database_name):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SHOW TABLES FROM `{database_name}`;")).fetchall()
            return {"tables": [row[0] for row in result]}
    except Exception as e:
        return {"error": str(e)}
    
#Function to list columns
def list_tables(database_name, table_name):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SHOW COLUMNS FROM `{database_name}`.`{table_name}`;")).fetchall()
            return {"columns": [row[0] for row in result]}
    except Exception as e:
        return {"error": str(e)}
'''


# Function to test connection
def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE();"))
            print(f"Connected to: {result.fetchone()[0]}")
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")

# Function to get schema
def get_schema():
    query = """
    SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = :database;
    """
    
    with engine.connect() as connection:
        result = connection.execute(text(query),{"database":MYSQL_DATABASE})
        schema_info = result.fetchall()
        
    schema_dict = {}
    for table, column, dtype in schema_info:
        if table not in schema_dict:
            schema_dict[table] = []
        schema_dict[table].append(f"{column} ({dtype})")
    
    return schema_dict

# Run connection test
if __name__=="__main__":
    test_connection()

 
