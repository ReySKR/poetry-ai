from enum import Enum

class MessageTypeEnum(Enum):
    """Enumeration for message types. Either AIMessage or HumanMessage."""
    AIMessage = 0
    HumanMessage = 1