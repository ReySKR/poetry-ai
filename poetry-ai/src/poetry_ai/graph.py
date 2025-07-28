from poetry_ai.tool import collaboration_assistance
from poetry_ai.prompt import sys_prompts
from poetry_ai.output_format import PoetryOutput
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os
load_dotenv()

_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=1.0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Prebuilt react agent since of simple hitl structure
_agent = create_react_agent(
    model=_llm,
    tools=[collaboration_assistance],
    checkpointer=InMemorySaver()
)

def start_chat(user_msg, thread_id):
    thread_config = {"configurable": {"thread_id": thread_id}}
    answer = _agent.invoke({"messages": [
        SystemMessage(sys_prompts["poetry"][1][0]),
        AIMessage("Hey! Ich bin für dich da um mit dir ein super tolles Gedicht zu zaubern! Um was soll es gehen? Gib mir einfach bescheid sobald du erste Ideen hast :-)"),
        HumanMessage(user_msg)
    ]}, thread_config)
    print(answer)
    return answer["messages"][-1]

def resume_chat(user_response, thread_id):
    thread_config = {"configurable": {"thread_id": thread_id}}
    answer = _agent.invoke(
        Command(resume=user_response), thread_config)
    print(answer)
    return answer["messages"][-1]

