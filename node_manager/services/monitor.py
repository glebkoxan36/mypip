"""
Сервис мониторинга транзакций
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TransactionMonitor:
    """Монитор транзакций через WebSocket"""
    
    def __init__(self, node, on_transaction: Callable = None):
        """
        Args:
            node: Экземпляр ноды
            on_transaction: Функция обратного вызова при новой транзакции
        """
        self.node = node
        self.on_transaction = on_transaction
        self.websocket = None
        self.connected = False
        self.subscribed_addresses = set()
        self._running = False
        self._reconnect_delay = 5
        self._max_reconnect_attempts = 10
        self._reconnect_attempts = 0
        
    async def start(self):
        """Запуск мониторинга"""
        if self._running:
            logger.warning("Monitor already running")
            return
        
        self._running = True
        asyncio.create_task(self._run())
    
    async def stop(self):
        """Остановка мониторинга"""
        self._running = False
        await self._disconnect()
    
    async def subscribe_address(self, address: str):
        """Подписаться на адрес"""
        self.subscribed_addresses.add(address)
        
        if self.connected and self.websocket:
            await self._send_subscription(address)
    
    async def unsubscribe_address(self, address: str):
        """Отписаться от адреса"""
        if address in self.subscribed_addresses:
            self.subscribed_addresses.remove(address)
        
        if self.connected and self.websocket:
            await self._send_unsubscription(address)
    
    async def _run(self):
        """Основной цикл мониторинга"""
        while self._running:
            try:
                await self._connect()
                await self._listen()
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await self._handle_error(e)
    
    async def _connect(self):
        """Подключение к WebSocket"""
        try:
            from ..api.websocket import WebSocketClient
            
            # Формируем WebSocket URL
            if self.node.blockbook_url:
                base_url = self.node.blockbook_url.replace('https://', 'wss://').replace('http://', 'ws://')
                ws_url = f"{base_url}/wss/{self.node.api_key}"
            else:
                # Fallback URL
                ws_url = f"wss://{self.node.coin_type.lower()}book.nownodes.io/wss/{self.node.api_key}"
            
            self.websocket = WebSocketClient(ws_url)
            await self.websocket.connect()
            
            self.connected = True
            self._reconnect_attempts = 0
            logger.info(f"WebSocket connected for {self.node.coin_type}")
            
            # Подписываемся на адреса
            for address in self.subscribed_addresses:
                await self._send_subscription(address)
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            self.connected = False
            raise
    
    async def _disconnect(self):
        """Отключение от WebSocket"""
        if self.websocket:
            await self.websocket.disconnect()
            self.websocket = None
            self.connected = False
            logger.info("WebSocket disconnected")
    
    async def _listen(self):
        """Прослушивание сообщений"""
        if not self.websocket:
            return
        
        async for message in self.websocket.listen():
            if not self._running:
                break
            
            try:
                await self._handle_message(message)
            except Exception as e:
                logger.error(f"Error handling message: {e}")
    
    async def _handle_message(self, message: str):
        """Обработка сообщения"""
        try:
            data = json.loads(message)
            
            # Определяем тип сообщения
            method = data.get('method')
            
            if method == 'subscribeAddresses':
                address_data = data.get('data', {})
                address = address_data.get('address')
                tx = address_data.get('tx', {})
                
                if address and tx and self.on_transaction:
                    # Получаем полную информацию о транзакции
                    tx_info = await self._get_transaction_details(tx.get('txid'))
                    if tx_info:
                        await self.on_transaction({
                            'address': address,
                            'transaction': tx_info,
                            'type': 'address_transaction'
                        })
            
            elif method == 'subscribeNewBlock':
                block_data = data.get('data', {})
                if block_data and self.on_transaction:
                    await self.on_transaction({
                        'block': block_data,
                        'type': 'new_block'
                    })
            
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON message: {message[:100]}")
        except Exception as e:
            logger.error(f"Message handling error: {e}")
    
    async def _send_subscription(self, address: str):
        """Отправка подписки на адрес"""
        if not self.websocket:
            return
        
        message = {
            "id": f"sub_{address}",
            "method": "subscribeAddresses",
            "params": {
                "addresses": [address]
            }
        }
        
        await self.websocket.send(json.dumps(message))
        logger.debug(f"Subscribed to address: {address}")
    
    async def _send_unsubscription(self, address: str):
        """Отправка отписки от адреса"""
        if not self.websocket:
            return
        
        message = {
            "id": f"unsub_{address}",
            "method": "unsubscribeAddresses",
            "params": {
                "addresses": [address]
            }
        }
        
        await self.websocket.send(json.dumps(message))
        logger.debug(f"Unsubscribed from address: {address}")
    
    async def _get_transaction_details(self, txid: str) -> Optional[Dict[str, Any]]:
        """Получить детали транзакции"""
        try:
            return await self.node.get_transaction(txid)
        except Exception as e:
            logger.error(f"Error getting transaction details: {e}")
            return None
    
    async def _handle_error(self, error: Exception):
        """Обработка ошибок"""
        await self._disconnect()
        
        if self._reconnect_attempts < self._max_reconnect_attempts:
            self._reconnect_attempts += 1
            delay = min(self._reconnect_delay * (2 ** self._reconnect_attempts), 300)
            
            logger.info(f"Reconnecting in {delay} seconds (attempt {self._reconnect_attempts})")
            await asyncio.sleep(delay)
        else:
            logger.error("Max reconnection attempts reached")
            self._running = False
    
    def is_running(self) -> bool:
        """Проверка работы монитора"""
        return self._running
    
    def get_subscribed_addresses(self) -> List[str]:
        """Получить список подписанных адресов"""
        return list(self.subscribed_addresses)
