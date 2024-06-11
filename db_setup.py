from langchain_community.utilities import SQLDatabase

def setup_database(database_name="Chinook.db"):
    db = SQLDatabase.from_uri("sqlite:///"+database_name)
    return db