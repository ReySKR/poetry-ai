from fastapi import FastAPI
import poetry_ai.graph as Agent

app = FastAPI()

@app.get("/start_chat/{thread_id}")
def start_chat(thread_id: int, user_message: str):
    return Agent.start_chat(user_message, thread_id)

@app.get("/resume_chat/{thread_id}")
def resume_chat(thread_id: int, user_message: str):
    return Agent.resume_chat(user_message, thread_id)
