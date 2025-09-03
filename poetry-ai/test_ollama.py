from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

_llm = ChatOllama(
    model="gpt-oss:20b"
)

messages = [HumanMessage("Was ist Winter?")]

message_stack = [
    SystemMessage("Beantworte die Frage"),
    HumanMessage(messages[0].content)
]
poetry = _llm.invoke(message_stack)

print(poetry)