from fastapi import FastAPI
from fastapi.logger import logger
import poetry_ai.graph as Agent

app = FastAPI()


@app.get("/start_chat/{thread_id}")
def start_chat(thread_id: int, user_message: str):
    logger.info(f"New Thread ID: {thread_id}")
    return Agent.start_chat(user_message, thread_id)


@app.get("/resume_chat/{thread_id}")
def resume_chat(thread_id: int, user_message: str):
    return Agent.resume_chat(user_message, thread_id)
