import os
from typing import List, Tuple, Optional, Union

import httpx
from poetry_tui.chat_components import MessageTypeEnum


class APIHandler:
    api_endpoint: str
    last_poetry: Union[str, None]

    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.api_endpoint = os.getenv("API_ENDPOINT")
        self.last_poetry = None

        if not self.api_endpoint:
            raise RuntimeError("API_ENDPOINT ist nicht gesetzt.")

        self._client_external = client is not None
        self._client = client or httpx.AsyncClient(base_url=self.api_endpoint, timeout=None)

    async def aclose(self) -> None:
        """Close client on with statement."""
        if not self._client_external and not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

    async def start_session(self, input: str, session_id: int) -> List[Tuple[MessageTypeEnum, str]]:
        resp = await self._client.get(f"/start_chat/{session_id}", params={"user_message": input})
        resp.raise_for_status()
        data = resp.json()
        self.last_poetry = data["last_poetry"]["content"]
        return [
            (
                MessageTypeEnum.HumanMessage if message["type"] == "human" else MessageTypeEnum.AIMessage,
                message["content"],
            )
            for message in data["messages"]
        ]

    async def resume_chat(self, input: int, session_id: int) -> Tuple[List[Tuple[MessageTypeEnum, str]], bool]:
        """Resumes chat. 2nd Tuple element signals end of chat!"""
        resp = await self._client.get(f"/resume_chat/{session_id}", params={"user_message": input})
        resp.raise_for_status()
        data = resp.json()
        self.last_poetry = data["last_poetry"]["content"]
        return (
            [
                (
                    MessageTypeEnum.HumanMessage if message["type"] == "human" else MessageTypeEnum.AIMessage,
                    message["content"],
                )
                for message in data["messages"]
            ],
            "__interrupt__" in data,
        )
