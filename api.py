from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from env_setup import setup_environment
from db_setup import setup_database
from llm_setup import setup_llm
from load_files_to_db import load_files_to_db
from langchain_community.agent_toolkits import create_sql_agent
import time
import uuid
import json
import logging
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import StreamingResponse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Global variables to store our setup
db = None
llm = None
agent_executor = None

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 100

@app.on_event("startup")
async def startup_event():
    global db, llm, agent_executor
    setup_environment()
    load_files_to_db('Database', 'Chinook_reduced.db')
    db = setup_database("Chinook_reduced.db")
    llm = setup_llm()
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)

@app.get("/v1/models")
async def get_models():
    return {"data": [{"id": "your-model-name", "object": "model", "created": int(time.time()), "owned_by": "your-organization"}]}

# @app.post("/v1/chat/completions")
# async def create_chat_completion(request: ChatCompletionRequest):
#     global agent_executor
#     if agent_executor is None:
#         raise HTTPException(status_code=500, detail="Agent not initialized")
    
#     # Combine all message contents into a single prompt
#     prompt = " ".join([msg.content for msg in request.messages])
#     result = agent_executor.invoke({"input": prompt})
    
#     # Parse the result, which is a string representation of a dict
#     try:
#         result_dict = json.loads(result['output'])
#     except json.JSONDecodeError:
#         # If it's not valid JSON, use the raw string
#         result_dict = {"text": result['output']}
    
#     # Construct the response using the format from your model
#     response = {
#         "id": f"chatcmpl-{uuid.uuid4()}",
#         "object": "chat.completion",
#         "created": int(time.time()),
#         "model": request.model,
#         "choices": [
#             {
#                 "index": 0,
#                 "message": {
#                     "role": "assistant",
#                     "content": result_dict.get("text", str(result_dict))
#                 },
#                 "finish_reason": "stop"
#             }
#         ],
#         "usage": result_dict.get("usage", {
#             "prompt_tokens": len(prompt.split()),
#             "completion_tokens": len(str(result_dict).split()),
#             "total_tokens": len(prompt.split()) + len(str(result_dict).split())
#         })
#     }
    
#     return response
# @app.post("/v1/chat/completions")
# async def create_chat_completion(request: ChatCompletionRequest):
#     logger.debug(f"Received request: {request}")
#     global agent_executor
#     if agent_executor is None:
#         raise HTTPException(status_code=500, detail="Agent not initialized")
    
#     # Combine all message contents into a single prompt
#     prompt = " ".join([msg.content for msg in request.messages])
#     result = agent_executor.invoke({"input": prompt})
    
#     # Extract the text content from the result
#     if isinstance(result, dict) and 'output' in result:
#         content = result['output']
#     else:
#         content = str(result)
    
#     # Construct a simpler response
#     response = {
#         "id": f"chatcmpl-{uuid.uuid4()}",
#         "object": "chat.completion",
#         "created": int(time.time()),
#         "model": request.model,
#         "choices": [
#             {
#                 "index": 0,
#                 "message": {
#                     "role": "assistant",
#                     "content": content
#                 },
#                 "finish_reason": "stop"
#             }
#         ],
#         "usage": {
#             "prompt_tokens": len(prompt.split()),
#             "completion_tokens": len(content.split()),
#             "total_tokens": len(prompt.split()) + len(content.split())
#         }
#         ,"text": "Hi"
#     }
#     logger.debug(f"Sending response: {response}")
#     return response
@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    global agent_executor
    if agent_executor is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    # Combine all message contents into a single prompt
    prompt = " ".join([msg.content for msg in request.messages])
    result = agent_executor.invoke({"input": prompt})
    
    # Extract the text content from the result
    if isinstance(result, dict) and 'output' in result:
        content = result['output']
    else:
        content = str(result)
    
    async def generate():
        yield json.dumps({
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": None
                }
            ]
        })
        yield json.dumps({
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }
            ]
        })

    return StreamingResponse(generate(), media_type="text/event-stream")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)