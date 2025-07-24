from langchain_core.tools import tool
from langgraph.types import interrupt

@tool
def collaboration_assistance(query: str) -> str:
    """
    Du kannst dieses Tool zur Kollaboration mit dem Nutzer nutzen.

    Input: Deine Frage zur Kollaboration
    Output: Antwort deiner Frage des Nutzers
    """
    hitl_response = interrupt(query)
    return hitl_response
     