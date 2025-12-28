"""
Фабрика для создания экземпляров нод
"""
import logging
from typing import Dict, Any, Type

from .base_node import BaseNode
from .litecoin import LitecoinNode
from .dogecoin import DogecoinNode
from .bitcoin import BitcoinNode
from ..utils.config import get_default_config

logger = logging.getLogger(__name__)

class NodeFactory:
    """Фабрика для создания нод"""
    
    # Реестр классов нод
    _node_classes: Dict[str, Type[BaseNode]] = {
        'LTC': LitecoinNode,
        'DOGE': DogecoinNode,
        'BTC': BitcoinNode,
    }
    
    # Конфигурации по умолчанию
    _default_configs = {
        'LTC': {
            'blockbook_url': 'https://ltcbook.nownodes.io',
            'rpc_url': 'https://ltc.nownodes.io',
            'network': 'mainnet',
            'decimals': 8,
            'coin_symbol': 'LTC',
            'coin_name': 'Litecoin'
        },
        'DOGE': {
            'blockbook_url': 'https://dogebook.nownodes.io',
            'rpc_url': 'https://doge.nownodes.io',
            'network': 'mainnet',
            'decimals': 8,
            'coin_symbol': 'DOGE',
            'coin_name': 'Dogecoin'
        },
        'BTC': {
            'blockbook_url': 'https://btcbook.nownodes.io',
            'rpc_url': 'https://btc.nownodes.io',
            'network': 'mainnet',
            'decimals': 8,
            'coin_symbol': 'BTC',
            'coin_name': 'Bitcoin'
        }
    }
    
    @classmethod
    def register_coin(cls, coin_symbol: str, node_class: Type[BaseNode], config: Dict[str, Any] = None):
        """
        Регистрация новой монеты
        
        Args:
            coin_symbol (str): Символ монеты
            node_class (Type[BaseNode]): Класс ноды
            config (Dict): Конфигурация по умолчанию
        """
        coin_symbol = coin_symbol.upper()
        cls._node_classes[coin_symbol] = node_class
        
        if config:
            cls._default_configs[coin_symbol] = config
        
        logger.info(f"Registered coin: {coin_symbol}")
    
    @classmethod
    def create(cls, 
               coin_type: str, 
               api_key: str = None,
               config: Dict[str, Any] = None,
               **kwargs) -> BaseNode:
        """
        Создать экземпляр ноды
        
        Args:
            coin_type (str): Тип монеты (LTC, DOGE, BTC)
            api_key (str): API ключ Nownodes
            config (Dict): Конфигурация
            **kwargs: Дополнительные параметры
        
        Returns:
            BaseNode: Экземпляр ноды
        """
        coin_type = coin_type.upper()
        
        if coin_type not in cls._node_classes:
            raise ValueError(
                f"Unsupported coin type: {coin_type}. "
                f"Supported: {', '.join(cls._node_classes.keys())}"
            )
        
        # Объединяем конфигурации
        final_config = {}
        
        # 1. Конфигурация по умолчанию
        if coin_type in cls._default_configs:
            final_config.update(cls._default_configs[coin_type])
        
        # 2. Переданная конфигурация
        if config:
            final_config.update(config)
        
        # 3. API ключ (обязательный параметр)
        if api_key:
            final_config['api_key'] = api_key
        elif 'api_key' not in final_config:
            raise ValueError("API key is required. Provide via api_key parameter or config.")
        
        # 4. Дополнительные параметры
        final_config.update(kwargs)
        
        # 5. Coin type
        final_config['coin_type'] = coin_type
        
        # Создаем экземпляр
        node_class = cls._node_classes[coin_type]
        node = node_class(**final_config)
        
        logger.info(f"Created {coin_type} node instance")
        return node
    
    @classmethod
    def get_supported_coins(cls) -> list:
        """Получить список поддерживаемых монет"""
        return list(cls._node_classes.keys())
    
    @classmethod
    def get_coin_config(cls, coin_type: str) -> Dict[str, Any]:
        """Получить конфигурацию по умолчанию для монеты"""
        coin_type = coin_type.upper()
        return cls._default_configs.get(coin_type, {})

# Упрощенная функция для быстрого создания
def create_node(coin_type: str, api_key: str = None, **kwargs) -> BaseNode:
    """
    Быстрое создание ноды
    
    Args:
        coin_type (str): Тип монеты
        api_key (str): API ключ
        **kwargs: Дополнительные параметры
    
    Returns:
        BaseNode: Экземпляр ноды
    """
    return NodeFactory.create(coin_type, api_key, **kwargs)
