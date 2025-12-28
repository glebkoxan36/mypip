"""
Базовый класс для всех криптовалютных нод
"""
import abc
import logging
from typing import Dict, List, Any, Optional, Union
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseNode(abc.ABC):
    """Абстрактный базовый класс ноды"""
    
    def __init__(self, 
                 coin_type: str,
                 api_key: str,
                 blockbook_url: str = None,
                 rpc_url: str = None,
                 network: str = "mainnet",
                 **kwargs):
        """
        Инициализация ноды
        
        Args:
            coin_type (str): Тип монеты (LTC, DOGE, BTC)
            api_key (str): API ключ Nownodes
            blockbook_url (str): URL Blockbook API
            rpc_url (str): URL RPC API
            network (str): Сеть (mainnet, testnet, regtest)
        """
        self.coin_type = coin_type.upper()
        self.api_key = api_key
        self.blockbook_url = blockbook_url
        self.rpc_url = rpc_url
        self.network = network
        self.headers = {"api-key": self.api_key}
        
        # Конфигурация монеты
        self.decimals = kwargs.get('decimals', 8)
        self.coin_symbol = kwargs.get('coin_symbol', self.coin_type)
        self.coin_name = kwargs.get('coin_name', self.coin_type)
        
        # Состояние
        self._connected = False
        self._last_error = None
        self._session = None
        
        # Клиенты
        self.rpc_client = None
        self.blockbook_client = None
        self.websocket_client = None
        
        # Инициализация клиентов
        self._init_clients()
    
    def _init_clients(self):
        """Инициализация клиентов"""
        from ..api.rpc import RPCClient
        from ..api.blockbook import BlockbookClient
        
        if self.rpc_url:
            self.rpc_client = RPCClient(self.rpc_url, self.headers)
        
        if self.blockbook_url:
            self.blockbook_client = BlockbookClient(self.blockbook_url, self.headers)
    
    @abc.abstractmethod
    async def connect(self) -> bool:
        """Подключение к ноде"""
        pass
    
    @abc.abstractmethod
    async def disconnect(self) -> bool:
        """Отключение от ноды"""
        pass
    
    # Основные методы (должны быть реализованы в наследниках)
    @abc.abstractmethod
    async def get_balance(self, address: str) -> Dict[str, Any]:
        """Получить баланс адреса"""
        pass
    
    @abc.abstractmethod
    async def get_address_info(self, address: str) -> Dict[str, Any]:
        """Получить информацию об адресе"""
        pass
    
    @abc.abstractmethod
    async def get_transaction(self, txid: str) -> Dict[str, Any]:
        """Получить информацию о транзакции"""
        pass
    
    @abc.abstractmethod
    async def get_address_utxos(self, address: str) -> List[Dict[str, Any]]:
        """Получить UTXO адреса"""
        pass
    
    @abc.abstractmethod
    async def send_transaction(self, raw_tx_hex: str) -> str:
        """Отправить сырую транзакцию"""
        pass
    
    @abc.abstractmethod
    async def create_raw_transaction(self, 
                                   inputs: List[Dict], 
                                   outputs: Dict[str, Union[float, Decimal]]) -> str:
        """Создать сырую транзакцию"""
        pass
    
    @abc.abstractmethod
    async def sign_raw_transaction(self, 
                                 raw_tx_hex: str, 
                                 private_keys: List[str] = None) -> Dict[str, Any]:
        """Подписать сырую транзакцию"""
        pass
    
    # Общие методы (реализация по умолчанию)
    async def validate_address(self, address: str) -> Dict[str, Any]:
        """Валидация адреса"""
        try:
            # Используем Blockbook для валидации
            if self.blockbook_client:
                info = await self.blockbook_client.get_address_info(address)
                if 'error' not in info:
                    return {
                        'is_valid': True,
                        'address': address,
                        'is_mine': False,
                        'is_script': False,
                        'is_witness': address.startswith(self._get_bech32_prefix())
                    }
            
            # Fallback на проверку формата
            from ..utils.validators import validate_crypto_address
            is_valid = validate_crypto_address(address, self.coin_type)
            
            return {
                'is_valid': is_valid,
                'address': address,
                'is_mine': False,
                'is_script': False,
                'is_witness': False
            }
            
        except Exception as e:
            logger.error(f"Error validating address: {e}")
            return {'is_valid': False, 'error': str(e)}
    
    async def estimate_fee(self, blocks: int = 3) -> Dict[str, Any]:
        """Оценить комиссию"""
        try:
            if self.rpc_client:
                result = await self.rpc_client.call("estimatesmartfee", [blocks])
                if 'error' not in result:
                    fee_data = result.get('result', {})
                    return {
                        'fee_per_kb': fee_data.get('feerate', 0.0001),
                        'blocks': blocks,
                        'coin': self.coin_type
                    }
            
            # Значения по умолчанию для каждой монеты
            default_fees = {
                'LTC': 0.0001,
                'DOGE': 1.0,
                'BTC': 0.00001
            }
            
            return {
                'fee_per_kb': default_fees.get(self.coin_type, 0.0001),
                'blocks': blocks,
                'coin': self.coin_type
            }
            
        except Exception as e:
            logger.error(f"Error estimating fee: {e}")
            return {'error': str(e)}
    
    async def get_blockchain_info(self) -> Dict[str, Any]:
        """Получить информацию о блокчейне"""
        try:
            if self.rpc_client:
                result = await self.rpc_client.call("getblockchaininfo", [])
                if 'error' not in result:
                    return result.get('result', {})
            
            return {
                'chain': self.network,
                'blocks': 0,
                'headers': 0,
                'difficulty': 0,
                'size_on_disk': 0
            }
            
        except Exception as e:
            logger.error(f"Error getting blockchain info: {e}")
            return {'error': str(e)}
    
    # Утилиты
    def is_connected(self) -> bool:
        """Проверка подключения"""
        return self._connected
    
    def get_coin_info(self) -> Dict[str, Any]:
        """Получить информацию о монете"""
        return {
            'symbol': self.coin_symbol,
            'name': self.coin_name,
            'type': self.coin_type,
            'network': self.network,
            'decimals': self.decimals,
            'blockbook_url': self.blockbook_url,
            'rpc_url': self.rpc_url
        }
    
    def satoshi_to_coin(self, satoshi: int) -> float:
        """Конвертировать сатоши в монеты"""
        return satoshi / (10 ** self.decimals)
    
    def coin_to_satoshi(self, amount: float) -> int:
        """Конвертировать монеты в сатоши"""
        return int(amount * (10 ** self.decimals))
    
    def _get_bech32_prefix(self) -> str:
        """Получить Bech32 префикс для монеты"""
        prefixes = {
            'LTC': 'ltc',
            'BTC': 'bc',
            'DOGE': ''  # Dogecoin не поддерживает Bech32
        }
        return prefixes.get(self.coin_type, '')
    
    async def batch_get_balances(self, addresses: List[str]) -> Dict[str, Dict[str, Any]]:
        """Пакетное получение балансов"""
        results = {}
        
        for address in addresses:
            try:
                balance = await self.get_balance(address)
                results[address] = balance
            except Exception as e:
                results[address] = {'error': str(e)}
        
        return results
    
    async def get_transaction_history(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить историю транзакций"""
        try:
            info = await self.get_address_info(address)
            transactions = info.get('transactions', [])
            return transactions[:limit]
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            return []
    
    def __str__(self) -> str:
        return f"{self.coin_name} Node ({self.network})"
    
    def __repr__(self) -> str:
        return f"<{self.coin_type}Node connected={self._connected}>"
