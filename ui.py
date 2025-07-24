import streamlit as st # type: ignore
import requests # type: ignore

# Set page title
st.title("🧠 AI-Powered SQL Query Generator")

# Input text box for user query
query_input = st.text_input("Enter your natural language query:")

if st.button("Generate SQL"):
    response = requests.post("http://127.0.0.1:8000/generate_sql/", json={"query": query_input})
    sql_query = response.json().get("sql_query", "Error generating query")
    st.code(sql_query, language="sql")

    # Store SQL query for execution
    st.session_state["generated_sql"] = sql_query
if "generated_sql" in st.session_state:
    if st.button("Execute SQL"):
        response = requests.post(
            "http://127.0.0.1:8000/execute_sql/",
            json={"query": st.session_state["generated_sql"]}
        )
        results = response.json().get("results", [])
        optimization_tips = response.json().get("optimization_tips", "No optimization tips available.")

        st.subheader("Query Results:")
        st.write(results)

        st.subheader("Optimization Tips:")
        st.write(optimization_tips)
