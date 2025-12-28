"""
Blockbook API клиент
"""
import aiohttp
import logging
from typing import Dict, Any, List
import asyncio

logger = logging.getLogger(__name__)

class BlockbookClient:
    """Клиент для Blockbook API"""
    
    def __init__(self, base_url: str, headers: Dict[str, str] = None):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def get_address_info(self, address: str) -> Dict[str, Any]:
        """Получить информацию об адресе"""
        url = f"{self.base_url}/api/v2/address/{address}"
        return await self._make_request(url)
    
    async def get_detailed_address_info(self, address: str) -> Dict[str, Any]:
        """Получить детальную информацию об адресе"""
        url = f"{self.base_url}/api/v2/address/{address}?details=txs"
        return await self._make_request(url)
    
    async def get_address_utxos(self, address: str) -> List[Dict[str, Any]]:
        """Получить UTXO адреса"""
        url = f"{self.base_url}/api/v2/utxo/{address}"
        result = await self._make_request(url)
        return result if isinstance(result, list) else []
    
    async def get_transaction(self, txid: str) -> Dict[str, Any]:
        """Получить информацию о транзакции"""
        url = f"{self.base_url}/api/v2/tx/{txid}"
        return await self._make_request(url)
    
    async def get_blockbook_info(self) -> Dict[str, Any]:
        """Получить информацию о Blockbook"""
        url = f"{self.base_url}/api/v2"
        return await self._make_request(url)
    
    async def get_block(self, height: int) -> Dict[str, Any]:
        """Получить информацию о блоке"""
        url = f"{self.base_url}/api/v2/block/{height}"
        return await self._make_request(url)
    
    async def get_xpub_info(self, xpub: str) -> Dict[str, Any]:
        """Получить информацию о xpub"""
        url = f"{self.base_url}/api/v2/xpub/{xpub}"
        return await self._make_request(url)
    
    async def search(self, query: str) -> Dict[str, Any]:
        """Поиск по блокчейну"""
        url = f"{self.base_url}/api/v2/search/{query}"
        return await self._make_request(url)
    
    async def _make_request(self, url: str) -> Dict[str, Any]:
        """Выполнить HTTP запрос"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Blockbook error {response.status}: {error_text}")
                    return {'error': f"HTTP {response.status}: {error_text}"}
                    
        except asyncio.TimeoutError:
            logger.error(f"Blockbook timeout for {url}")
            return {'error': 'Request timeout'}
        except Exception as e:
            logger.error(f"Blockbook request error: {e}")
            return {'error': str(e)}
    
    async def close(self):
        """Закрыть сессию"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def __del__(self):
        """Деструктор"""
        if self.session and not self.session.closed:
            asyncio.create_task(self.close())
