from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException
from query_generator import generate_sql_query, execute_query

# Initialize FastAPI app
app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/generate_sql/")
async def generate_sql(request: QueryRequest):
    """Generate SQL query from natural language input."""
    sql_query = generate_sql_query(request.query)
    if not sql_query:
        return { "error": "Failed to generate SQL" }
    return { "sql_query": sql_query }

@app.post("/execute_sql/")
async def execute_sql(request: QueryRequest):
    """Execute a given SQL query and return results."""
    sql_query = request.query
    try:
        
        results = execute_query(sql_query)
        
        if results is None:
            raise HTTPException(status_code=500, detail="Error executing query")
        
        #Ensure proper JSON serialization
        serialized_results = [dict(row._mapping) for row in results["results"]]
        
        return {
         "results": serialized_results,
         "optimization_tips": results["optimization_tips"]
        }
        
    except  Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#Run the FastAPI app
if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)