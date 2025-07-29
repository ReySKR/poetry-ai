from typing import TypedDict, List
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage

class State(TypedDict):
    messages: List[BaseMessage]
    last_poetry: AIMessage
    last_criticism: str
    history_rewritten_criticism: str