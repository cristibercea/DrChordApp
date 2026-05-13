import logging
from fastapi import WebSocket


class ConnectionManager:
    """WebSocket connection manager class"""
    def __init__(self): self.__active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        """
        Connects to websocket and stores the connection details
        :param websocket: WebSocket object
        :param user_id: User's ID
        :return: None
        """
        logging.info(f"[{self.__class__.__name__}]: Connecting to websocket {websocket.url}...")
        await websocket.accept()
        self.__active_connections[user_id] = websocket
        logging.info(f"[{self.__class__.__name__}]: Connected to websocket {websocket.url}.")

    def disconnect(self, user_id: int) -> None:
        """
        Disconnects from websocket and deletes the connection details
        :param user_id: User's ID
        :return: None
        """
        logging.info(f"[{self.__class__.__name__}]: Disconnecting from websocket of user with id {user_id}...")
        if user_id in self.__active_connections:
            del self.__active_connections[user_id]
            logging.info(f"[{self.__class__.__name__}]: Disconnected from websocket of user with id {user_id}.")
            return
        logging.error(f"[{self.__class__.__name__}]: Failed to disconnect from websocket of user with id {user_id}.")

    async def send_personal_message(self, message: str, user_id: int) -> None:
        """
        Sends a message to the websocket on a user's connection
        :param message: Message to send
        :param user_id: User's ID
        :return: None
        """
        logging.info(f"[{self.__class__.__name__}]: Sending message to user with id {user_id}...")
        if user_id in self.__active_connections:
            await self.__active_connections[user_id].send_text(message)
            logging.info(f"[{self.__class__.__name__}]: Sent message to user with id {user_id}.")
            return
        logging.error(f"[{self.__class__.__name__}]: Failed to send message to user with id {user_id}.")

ws_manager = ConnectionManager()