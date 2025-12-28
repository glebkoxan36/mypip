"""
RPC клиент для работы с Nownodes API
"""
import aiohttp
import json
import logging
from typing import Dict, Any, List
import asyncio

logger = logging.getLogger(__name__)

class RPCClient:
    """Асинхронный RPC клиент"""
    
    def __init__(self, rpc_url: str, headers: Dict[str, str] = None):
        self.rpc_url = rpc_url
        self.headers = headers or {}
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    async def call(self, method: str, params: List[Any] = None) -> Dict[str, Any]:
        """
        Выполнить RPC вызов
        
        Args:
            method (str): Название метода
            params (list): Параметры
        
        Returns:
            dict: Результат
        """
        if params is None:
            params = []
        
        payload = {
            "jsonrpc": "1.0",
            "id": "node_manager",
            "method": method,
            "params": params
        }
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(
                self.rpc_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Проверяем наличие ошибки в ответе
                    if 'error' in result and result['error'] is not None:
                        logger.error(f"RPC error for {method}: {result['error']}")
                        return {'error': result['error']}
                    
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"HTTP error {response.status} for {method}: {error_text}")
                    return {'error': f"HTTP {response.status}: {error_text}"}
                    
        except asyncio.TimeoutError:
            logger.error(f"RPC timeout for {method}")
            return {'error': 'Request timeout'}
        except Exception as e:
            logger.error(f"RPC call error for {method}: {e}")
            return {'error': str(e)}
    
    async def batch_call(self, calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Пакетный RPC вызов
        
        Args:
            calls (list): Список вызовов [{'method': '...', 'params': [...]}]
        
        Returns:
            list: Результаты
        """
        if not calls:
            return []
        
        payload = []
        for i, call in enumerate(calls):
            payload.append({
                "jsonrpc": "1.0",
                "id": i,
                "method": call['method'],
                "params": call.get('params', [])
            })
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.post(
                self.rpc_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            ) as response:
                if response.status == 200:
                    results = await response.json()
                    return results
                else:
                    error_text = await response.text()
                    logger.error(f"Batch RPC error: HTTP {response.status}: {error_text}")
                    return [{'error': f"HTTP {response.status}"} for _ in calls]
                    
        except Exception as e:
            logger.error(f"Batch RPC error: {e}")
            return [{'error': str(e)} for _ in calls]
    
    async def close(self):
        """Закрыть сессию"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def __del__(self):
        """Деструктор"""
        if self.session and not self.session.closed:
            asyncio.create_task(self.close())
