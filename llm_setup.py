from langchain_openai import ChatOpenAI

def setup_llm():
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    return llm