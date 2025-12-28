"""
Node Manager - Универсальный модуль для работы с криптовалютными нодами
Поддерживает: Litecoin, Dogecoin, Bitcoin, и другие через Nownodes API
"""

__version__ = "2.0.0"
__author__ = "Crypto Node Manager Team"

from .core.node_factory import NodeFactory, create_node
from .core.base_node import BaseNode
from .services.monitor import TransactionMonitor
from .services.collector import FundsCollector
from .utils.exceptions import NodeError, ConnectionError, TransactionError
from .utils.config import load_config, get_coin_config

__all__ = [
    'NodeFactory',
    'create_node',
    'BaseNode',
    'TransactionMonitor',
    'FundsCollector',
    'NodeError',
    'ConnectionError',
    'TransactionError',
    'load_config',
    'get_coin_config'
]

# Упрощенный интерфейс для быстрого старта
def get_node_manager(coin: str, api_key: str = None, **kwargs):
    """
    Быстрое создание менеджера нод
    
    Args:
        coin (str): Тип монеты ('LTC', 'DOGE', 'BTC')
        api_key (str): API ключ Nownodes
        **kwargs: Дополнительные параметры
    
    Returns:
        BaseNode: Экземпляр ноды
    """
    return create_node(coin, api_key, **kwargs)
