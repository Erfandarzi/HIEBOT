import os
from dotenv import load_dotenv

load_dotenv()  # This loads environment variables from .env into the environment

def setup_environment():
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key is None:
        raise ValueError("API Key is not set in the environment variables")
    os.environ["OPENAI_API_KEY"] = api_key
