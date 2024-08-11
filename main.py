from env_setup import setup_environment
from db_setup import setup_database
from llm_setup import setup_llm
from chain_setup import setup_chain
from load_files_to_db import load_files_to_db
from operator import itemgetter
from langchain.chains import create_sql_query_chain
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_openai_tools_agent
from langchain.agents.agent import AgentExecutor
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.schema.runnable.config import RunnableConfig
from langchain.prompts import ChatPromptTemplate
import asyncio


def main():
    setup_environment()
    load_files_to_db('Database', 'Chinook.db')

    db = setup_database("Chinook.db")
    llm = setup_llm()
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)

    agent_executor.invoke(
        {
            "input": '''
Calculate the odds ratio for poor outcomes (defined as MRI score > 2)
based on cord blood pH levels'''

        }
    )
if __name__ == "__main__":
    main()  