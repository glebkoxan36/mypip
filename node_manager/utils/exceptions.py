"""
Кастомные исключения модуля
"""

class NodeError(Exception):
    """Базовое исключение для ошибок ноды"""
    pass

class ConnectionError(NodeError):
    """Ошибка подключения"""
    pass

class TransactionError(NodeError):
    """Ошибка транзакции"""
    pass

class ValidationError(NodeError):
    """Ошибка валидации"""
    pass

class ConfigurationError(NodeError):
    """Ошибка конфигурации"""
    pass

class RPCError(NodeError):
    """Ошибка RPC вызова"""
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code

class BlockbookError(NodeError):
    """Ошибка Blockbook API"""
    pass

class WebSocketError(NodeError):
    """Ошибка WebSocket"""
    pass

class CollectionError(NodeError):
    """Ошибка сбора средств"""
    pass

class InsufficientFundsError(NodeError):
    """Недостаточно средств"""
    pass
