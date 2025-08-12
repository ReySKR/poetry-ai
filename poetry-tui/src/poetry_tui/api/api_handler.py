import requests
import os
from typing import List, Tuple

from poetry_tui.chat_components import MessageTypeEnum


class APIHandler:
    def __init__(self, session_id: int):
        self._session_id = session_id
        self.api_endpoint = os.getenv("API_ENDPOINT")

    def start_session(self, input: str) -> List[Tuple[MessageTypeEnum, str]]:
        response = requests.get(f"{self.api_endpoint}/start_chat/{self._session_id}", params={"user_message": input}).json()
        return [(MessageTypeEnum.HumanMessage if message["type"] == "human" else MessageTypeEnum.AIMessage, message["content"]) for message in response["messages"]]

    def resume_chat(self, input: int) -> Tuple[List[Tuple[MessageTypeEnum, str]], bool]:
        """Resumes chat. 2nd Tuple element signals end of chat!"""
        response = requests.get(f"{self.api_endpoint}/resume_chat/{self._session_id}", params={"user_message": input}).json()
        return (
            [(MessageTypeEnum.HumanMessage if message["type"] == "human" else MessageTypeEnum.AIMessage,
              message["content"]) for message in response["messages"]],
            "__interrupt__" in response
        )



