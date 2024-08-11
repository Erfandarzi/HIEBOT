import chainlit as cl
import requests  # Import requests to make HTTP calls to your FastAPI backend

@cl.on_chat_start
async def start_chat():
    # This is the initial message to the user
    await cl.Message(content="Welcome! Please type your query:").send()

@cl.on_message
async def handle_message(message: cl.Message):
    # Send user input to FastAPI backend and await the response
    response = requests.post('http://localhost:8000/query/', json={"query": message.content})
    # Assume the response from the backend is JSON with a 'response' key
    if response.status_code == 200:
        backend_response = response.json()['response']
        await cl.Message(content=backend_response).send()
    else:
        await cl.Message(content="Sorry, there was an error processing your request.").send()
