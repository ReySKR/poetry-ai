from poetry_ai.tool import collaboration_assistance
from poetry_ai.prompt import sys_prompts
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
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

def get_poetry(user_msg):
    thread_config = {"configurable": {"thread_id": "1"}}
    answer = _agent.invoke({"messages": [
        SystemMessage(sys_prompts["poetry"][0]),
        AIMessage("Hey! Ich bin für dich da um mit dir ein super tolles Gedicht zu zaubern! Um was soll es gehen? Gib mir einfach bescheid sobald du erste Ideen hast :-)"),
        HumanMessage(user_msg)
    ]}, thread_config)
    return answer

print(get_poetry(input("msg:")))

