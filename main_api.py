import requests
import asyncio
import chainlit as cl

API_URL = "http://localhost:8000/query"

@cl.on_message
async def main(message: str):
    response = requests.post(API_URL, json={"input": message})
    result = response.json()["result"]
    await cl.Message(content=result).send()

if __name__ == "__main__":
    cl.run(main)