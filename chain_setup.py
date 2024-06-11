from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_community.agent_toolkits import SQLDatabaseToolkit

def setup_chain(llm, db):
    # Create the SQL query chain
    write_query = create_sql_query_chain(llm, db)
    
    # Define the answer prompt template
    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
    )
    
    # Set up the query execution tool
    execute_query = QuerySQLDataBaseTool(db=db)
    
    # Define the final chain with the answer prompt and output parser
    answer = answer_prompt | llm | StrOutputParser()
    chain = (
        RunnablePassthrough.assign(query=write_query).assign(
            result=itemgetter("query") | execute_query
        )
        | answer
    )
    
    
    return chain