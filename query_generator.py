import os
import openai # type: ignore
import sqlparse # type: ignore
import re
from dotenv import load_dotenv # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.exc import SQLAlchemyError # type: ignore
from database import engine, list_databases, list_tables, list_columns

#Load environment variables
load_dotenv()

#OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Setting Limits toavoid token limit issues
MAX_TABLES = 5
MAX_COLUMNS_PER_TABLE = 5

def get_limited_schema():
    """Fetches a reduced database schema to fit within OpenAI's token limits."""
    schema = {}
    databases = list_databases().get("databases", [])

    for db in databases:
        schema[db] = {}
        tables = list_tables(db).get("tables", [])[:MAX_TABLES]

        for table in tables:
            schema[db][table] = list_columns(db, table).get("columns", [])[:MAX_COLUMNS_PER_TABLE]

    return schema


def clean_sql_output(response_text):
    """extracts the raw SQL query."""
    #Removes Markdoen code block formatiing (```sql...```)
    clean_query = re.sub(r"```sql\n(.*?)\n```", r"\1", response_text, flags = re.DOTALL)
    
    #Extract only valid SQL (handles AI explanations)
    sql_match = re.search(r"SELECT .*?;", clean_query, re.DOTALL | re.IGNORECASE)
    
    return sql_match.group(0) if sql_match else clean_query.strip()

'''def validate_sql_query(sql_query):
    """Validates the SQL query syntax before execution."""
    try:
        parsed = sqlparse.parse(sql_query)
        if not parsed:
            return False, "Invalid SQL syntax."
        return True, None
    except Exception as e:
        return False, str(e)'''

def generate_sql_query(nl_query):
    """Converts natural language query to an optimized SQL query."""
    schema = get_limited_schema()

    schema_text = "\n".join([f"{db}.{table}: {', '.join(columns)}" for db, tables in schema.items() for table, columns in tables.items()])
    
    prompt = f"""
    You are an SQL expert. Convert the following natural language query into an optimized MySQL query.
    Ensure:
    - Proper use of INDEXING where applicable.
    - Use of efficient JOINS instead of nested queries.
    - Use GROUP BY when aggregations are needed.
    - Ensure SQL is valid and optimized for execution.

    Database Schema:
    {schema_text}
    
    User Request: {nl_query}
    
    SQL Query:
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a SQL optimization expert."},
                {"role": "user", "content": prompt}
            ]
        )

        raw_sql_query = response.choices[0].message.content.strip()

        # Clean the response to extract only the SQL query
        clean_query = clean_sql_output(raw_sql_query)
        print("logging:",clean_query)
        return clean_query

    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return None


def execute_query(sql_query):
    """Executes a validated and optimized SQL query."""
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            rows = result.fetchall()
            
            #Get column names
            column_names = result.keys()
            
            # Convert results into a list of dictionaries
            formatted_results = [dict(zip(column_names, row)) for row in rows]
            
        return {"results": formatted_results}
    
    except SQLAlchemyError as e:
        return {"error": str(e)} 


