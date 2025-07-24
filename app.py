from fastapi import FastAPI # type: ignore
import logging
from database import list_databases, list_tables, list_columns
from pydantic import BaseModel # type: ignore
from fastapi import HTTPException, Query # type: ignore
from query_generator import generate_sql_query, execute_query

# Initialize FastAPI app
app = FastAPI()

#Configure Logging

logging.basicConfig(level=logging.DEBUG)

# API-Listing all the Databases
@app.get("/list_databases/")
def get_databases():
    return list_databases()

# API call to list all tables in a database
@app.get("/list_tables/{database_name}")
def get_tables(database_name: str):
    return list_tables(database_name)

# API call to list all columns in a table
@app.get("/list_columns/{database_name}/{table_name}")
def get_columns(database_name: str, table_name: str):
    return list_columns(database_name, table_name)

# API: Generate SQL query from Natural Language

@app.post("/generate_sql/")
async def generate_sql(natural_language_query: str):
    """Generate SQL query from natural language input."""
    logging.debug(f"Generating SQL Query for: {natural_language_query}")
    sql_query = generate_sql_query(natural_language_query)
    
    if sql_query:
        return {"sql_query": sql_query}
    return {"error:" "Failed to generate SQL"}

# API: Execute SQL query 

@app.post("/execute_sql/")
def execute_sql(sql_query: str = Query(..., description = " SQL query to execute")):
    """Execute a given SQL query and return results."""
    result = execute_query(sql_query)
    return result 