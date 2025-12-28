"""
WebSocket клиент
"""
import asyncio
import logging
from typing import AsyncGenerator

import websockets

logger = logging.getLogger(__name__)

class WebSocketClient:
    """Клиент для WebSocket соединений"""
    
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.websocket = None
        self.connected = False
    
    async def connect(self):
        """Подключение к WebSocket"""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.connected = True
            logger.info(f"WebSocket connected to {self.ws_url}")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            raise
    
    async def disconnect(self):
        """Отключение от WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("WebSocket disconnected")
    
    async def send(self, message: str):
        """Отправка сообщения"""
        if self.connected and self.websocket:
            await self.websocket.send(message)
    
    async def listen(self) -> AsyncGenerator[str, None]:
        """Прослушивание сообщений"""
        if not self.connected or not self.websocket:
            return
        
        try:
            async for message in self.websocket:
                yield message
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.connected = False
        except Exception as e:
            logger.error(f"WebSocket listen error: {e}")
            self.connected = False
