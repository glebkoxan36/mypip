"""
Веб-сервер и API для управления Node Manager
"""
import asyncio
import json
import logging
import secrets
import hashlib
import base64
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

import aiohttp
from aiohttp import web
import aiohttp_cors
import jwt
import bcrypt
import psutil
import platform

# Добавляем родительский каталог в путь для импорта
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from node_manager import NodeManager, create_node_manager
except ImportError:
    # Для разработки
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from node_manager import NodeManager, create_node_manager
logger = logging.getLogger(__name__)

@dataclass
class WebConfig:
    """Конфигурация веб-сервера"""
    host: str = "0.0.0.0"
    port: int = 8080
    api_prefix: str = "/api/v1"
    enable_web_ui: bool = True
    enable_api: bool = True
    allow_cors: bool = True
    cors_origins: List[str] = None
    session_timeout: int = 3600  # 1 час
    rate_limit: int = 100  # запросов в минуту
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000", "http://localhost:8080"]

@dataclass
class AuthConfig:
    """Конфигурация аутентификации"""
    enabled: bool = True
    admin_username: str = "admin"
    admin_password_hash: str = ""  # bcrypt хэш
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    
    def __post_init__(self):
        if not self.jwt_secret:
            self.jwt_secret = secrets.token_urlsafe(32)

class WebServer:
    """Веб-сервер для управления Node Manager"""
    
    def __init__(self, node_manager: NodeManager = None, config: Dict[str, Any] = None):
        """
        Инициализация веб-сервера
        
        Args:
            node_manager: Экземпляр NodeManager
            config: Конфигурация веб-сервера
        """
        self.node_manager = node_manager or NodeManager()
        self.config = self._load_config(config)
        self.auth_config = self._load_auth_config(config)
        
        # Веб-приложение
        self.app = web.Application()
        self.runner = None
        self.site = None
        
        # Хранилище сессий (в продакшене использовать Redis)
        self.sessions = {}
        self.rate_limits = {}
        
        # API роуты
        self.setup_routes()
        
        # Запускаем фоновые задачи
        self.background_tasks = []
        
        # Время запуска
        self.start_time = datetime.now()
        
        logger.info(f"Web server initialized on {self.config.host}:{self.config.port}")
    
    def _load_config(self, config: Dict[str, Any]) -> WebConfig:
        """Загрузка конфигурации веб-сервера"""
        if not config:
            config = {}
        
        # Берем настройки из конфига Node Manager
        nm_config = self.node_manager.config
        web_config = nm_config.get('web_server', {})
        
        return WebConfig(
            host=web_config.get('host', config.get('host', '0.0.0.0')),
            port=web_config.get('port', config.get('port', 8080)),
            api_prefix=web_config.get('api_prefix', config.get('api_prefix', '/api/v1')),
            enable_web_ui=web_config.get('enable_web_ui', config.get('enable_web_ui', True)),
            enable_api=web_config.get('enable_api', config.get('enable_api', True)),
            allow_cors=web_config.get('allow_cors', config.get('allow_cors', True)),
            cors_origins=web_config.get('cors_origins', config.get('cors_origins', ['http://localhost:3000'])),
            session_timeout=web_config.get('session_timeout', config.get('session_timeout', 3600)),
            rate_limit=web_config.get('rate_limit', config.get('rate_limit', 100))
        )
    
    def _load_auth_config(self, config: Dict[str, Any]) -> AuthConfig:
        """Загрузка конфигурации аутентификации"""
        if not config:
            config = {}
        
        nm_config = self.node_manager.config
        auth_config = nm_config.get('auth', {})
        
        # Пароль можно установить через переменную окружения
        admin_password = auth_config.get('admin_password') or os.getenv('NODE_MANAGER_ADMIN_PASSWORD')
        
        if admin_password:
            # Хэшируем пароль если он в открытом виде
            password_hash = self._hash_password(admin_password)
        else:
            password_hash = auth_config.get('admin_password_hash', '')
        
        return AuthConfig(
            enabled=auth_config.get('enabled', config.get('auth_enabled', True)),
            admin_username=auth_config.get('admin_username', config.get('admin_username', 'admin')),
            admin_password_hash=password_hash,
            jwt_secret=auth_config.get('jwt_secret', config.get('jwt_secret', secrets.token_urlsafe(32))),
            jwt_algorithm=auth_config.get('jwt_algorithm', config.get('jwt_algorithm', 'HS256'))
        )
    
    def setup_routes(self):
        """Настройка маршрутов"""
        # API роуты
        if self.config.enable_api:
            self.setup_api_routes()
        
        # Веб-интерфейс
        if self.config.enable_web_ui:
            self.setup_web_routes()
        
        # Настройка CORS
        if self.config.allow_cors:
            self.setup_cors()
        
        # Middleware для аутентификации и rate limiting
        self.app.middlewares.append(self.auth_middleware)
        self.app.middlewares.append(self.rate_limit_middleware)
        self.app.middlewares.append(self.error_middleware)
    
    def setup_api_routes(self):
        """Настройка API маршрутов"""
        api = self.config.api_prefix
        
        # Аутентификация
        self.app.router.add_post(f'{api}/auth/login', self.api_login)
        self.app.router.add_post(f'{api}/auth/logout', self.api_logout)
        self.app.router.add_get(f'{api}/auth/check', self.api_check_auth)
        
        # Статус и информация
        self.app.router.add_get(f'{api}/status', self.api_status)
        self.app.router.add_get(f'{api}/stats', self.api_stats)
        self.app.router.add_get(f'{api}/coins', self.api_get_coins)
        self.app.router.add_get(f'{api}/nodes', self.api_get_nodes)
        
        # Управление нодами
        self.app.router.add_post(f'{api}/nodes/{{coin}}/connect', self.api_connect_node)
        self.app.router.add_post(f'{api}/nodes/{{coin}}/disconnect', self.api_disconnect_node)
        self.app.router.add_get(f'{api}/nodes/{{coin}}/info', self.api_get_node_info)
        
        # Балансы и транзакции
        self.app.router.add_get(f'{api}/nodes/{{coin}}/balance/{{address}}', self.api_get_balance)
        self.app.router.add_get(f'{api}/nodes/{{coin}}/transactions/{{address}}', self.api_get_transactions)
        self.app.router.add_get(f'{api}/nodes/{{coin}}/utxos/{{address}}', self.api_get_utxos)
        
        # Мониторинг
        self.app.router.add_post(f'{api}/monitoring/start', self.api_start_monitoring)
        self.app.router.add_post(f'{api}/monitoring/stop', self.api_stop_monitoring)
        self.app.router.add_post(f'{api}/monitoring/address', self.api_monitor_address)
        self.app.router.add_delete(f'{api}/monitoring/address', self.api_unmonitor_address)
        
        # Сбор средств
        self.app.router.add_post(f'{api}/collection/collect', self.api_collect_funds)
        self.app.router.add_post(f'{api}/collection/estimate', self.api_estimate_collection)
        self.app.router.add_get(f'{api}/collection/status', self.api_collection_status)
        
        # Конфигурация
        self.app.router.add_get(f'{api}/config', self.api_get_config)
        self.app.router.add_put(f'{api}/config', self.api_update_config)
        self.app.router.add_post(f'{api}/config/reload', self.api_reload_config)
        self.app.router.add_post(f'{api}/config/save', self.api_save_config)
        
        # Логи
        self.app.router.add_get(f'{api}/logs', self.api_get_logs)
        self.app.router.add_get(f'{api}/logs/stream', self.api_stream_logs)
        
        # Система
        self.app.router.add_post(f'{api}/system/restart', self.api_restart)
        self.app.router.add_post(f'{api}/system/shutdown', self.api_shutdown)
        self.app.router.add_get(f'{api}/system/info', self.api_system_info)
        
        # WebSocket для реального времени
        self.app.router.add_get(f'{api}/ws', self.api_websocket)
    
    def setup_web_routes(self):
        """Настройка маршрутов веб-интерфейса"""
        # Статические файлы (если есть)
        static_dir = Path(__file__).parent / 'static'
        if static_dir.exists():
            self.app.router.add_static('/static/', static_dir)
        
        # Главная страница
        self.app.router.add_get('/', self.web_index)
        self.app.router.add_get('/dashboard', self.web_dashboard)
        self.app.router.add_get('/nodes', self.web_nodes)
        self.app.router.add_get('/monitoring', self.web_monitoring)
        self.app.router.add_get('/collection', self.web_collection)
        self.app.router.add_get('/config', self.web_config)
        self.app.router.add_get('/logs', self.web_logs)
        self.app.router.add_get('/login', self.web_login)
        self.app.router.add_get('/logout', self.web_logout)
    
    def setup_cors(self):
        """Настройка CORS"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })
        
        # Применяем CORS ко всем маршрутам
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    @web.middleware
    async def auth_middleware(self, request: web.Request, handler):
        """Middleware для аутентификации"""
        # Публичные маршруты
        public_routes = [
            f'{self.config.api_prefix}/auth/login',
            f'{self.config.api_prefix}/auth/check',
            '/login',
            '/static/',
            '/favicon.ico'
        ]
        
        # Проверяем публичный ли маршрут
        for route in public_routes:
            if request.path.startswith(route):
                return await handler(request)
        
        # Если аутентификация отключена, пропускаем
        if not self.auth_config.enabled:
            request['user'] = {'username': 'admin', 'role': 'admin'}
            return await handler(request)
        
        # Проверяем аутентификацию для API
        if request.path.startswith(self.config.api_prefix):
            auth_header = request.headers.get('Authorization')
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]
                if self._verify_jwt(token):
                    # Добавляем пользователя в запрос
                    request['user'] = self._decode_jwt(token)
                    return await handler(request)
            
            return web.json_response(
                {'error': 'Unauthorized', 'message': 'Invalid or missing token'},
                status=401
            )
        
        # Для веб-интерфейса проверяем сессию
        session_id = request.cookies.get('session_id')
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            if datetime.now() < session['expires']:
                # Обновляем сессию
                session['expires'] = datetime.now() + timedelta(seconds=self.config.session_timeout)
                request['user'] = session['user']
                return await handler(request)
        
        # Редирект на страницу логина для веб-интерфейса
        if self.config.enable_web_ui:
            return web.HTTPFound('/login')
        
        return web.json_response(
            {'error': 'Unauthorized', 'message': 'Authentication required'},
            status=401
        )
    
    @web.middleware
    async def rate_limit_middleware(self, request: web.Request, handler):
        """Middleware для ограничения запросов"""
        if not self.config.rate_limit:
            return await handler(request)
        
        client_ip = request.remote
        path = request.path
        
        # Ключ для rate limiting
        key = f"{client_ip}:{path}"
        
        now = datetime.now()
        window_start = now - timedelta(minutes=1)
        
        # Очищаем старые записи
        if key in self.rate_limits:
            self.rate_limits[key] = [
                timestamp for timestamp in self.rate_limits[key]
                if timestamp > window_start
            ]
        
        # Проверяем лимит
        if key in self.rate_limits and len(self.rate_limits[key]) >= self.config.rate_limit:
            return web.json_response(
                {'error': 'Rate limit exceeded', 'message': 'Too many requests'},
                status=429
            )
        
        # Добавляем запрос
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        self.rate_limits[key].append(now)
        
        # Ограничиваем размер истории
        if len(self.rate_limits[key]) > self.config.rate_limit * 2:
            self.rate_limits[key] = self.rate_limits[key][-self.config.rate_limit:]
        
        return await handler(request)
    
    @web.middleware
    async def error_middleware(self, request: web.Request, handler):
        """Middleware для обработки ошибок"""
        try:
            response = await handler(request)
            return response
        except web.HTTPException as e:
            return e
        except Exception as e:
            logger.error(f"Error in handler {request.path}: {e}", exc_info=True)
            return web.json_response(
                {'error': 'Internal server error', 'message': str(e)},
                status=500
            )
    
    # API методы
    async def api_login(self, request: web.Request) -> web.Response:
        """API: Аутентификация"""
        try:
            data = await request.json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return web.json_response(
                    {'error': 'Missing credentials'},
                    status=400
                )
            
            # Проверяем учетные данные
            if not self._check_credentials(username, password):
                return web.json_response(
                    {'error': 'Invalid credentials'},
                    status=401
                )
            
            # Создаем JWT токен
            token = self._create_jwt(username)
            
            # Для веб-интерфейса создаем сессию
            session_id = secrets.token_urlsafe(32)
            self.sessions[session_id] = {
                'user': username,
                'created': datetime.now(),
                'expires': datetime.now() + timedelta(seconds=self.config.session_timeout)
            }
            
            response_data = {
                'success': True,
                'token': token,
                'user': {
                    'username': username,
                    'role': 'admin'
                }
            }
            
            response = web.json_response(response_data)
            
            # Устанавливаем cookie для веб-интерфейса
            response.set_cookie(
                'session_id',
                session_id,
                httponly=True,
                max_age=self.config.session_timeout,
                samesite='Strict'
            )
            
            return response
            
        except json.JSONDecodeError:
            return web.json_response(
                {'error': 'Invalid JSON'},
                status=400
            )
        except Exception as e:
            logger.error(f"Login error: {e}")
            return web.json_response(
                {'error': 'Login failed'},
                status=500
            )
    
    async def api_logout(self, request: web.Request) -> web.Response:
        """API: Выход из системы"""
        session_id = request.cookies.get('session_id')
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        response = web.json_response({'success': True})
        response.del_cookie('session_id')
        return response
    
    async def api_check_auth(self, request: web.Request) -> web.Response:
        """API: Проверка аутентификации"""
        if not self.auth_config.enabled:
            return web.json_response({
                'authenticated': True,
                'user': {'username': 'admin', 'role': 'admin'}
            })
        
        return web.json_response({
            'authenticated': 'user' in request,
            'user': request.get('user', {})
        })
    
    async def api_status(self, request: web.Request) -> web.Response:
        """API: Получение статуса системы"""
        stats = await self.node_manager.get_stats()
        
        # Добавляем дополнительную информацию
        status = {
            'version': '2.1.0',
            'timestamp': datetime.now().isoformat(),
            'uptime': str(datetime.now() - self.start_time),
            'manager': {
                'connected': stats['total_nodes'] > 0,
                'monitoring': len(self.node_manager._monitors) > 0,
                'collection': self.node_manager._is_running
            },
            'nodes': stats['nodes'],
            'enabled_coins': stats['enabled_coins'],
            'web_server': {
                'host': self.config.host,
                'port': self.config.port,
                'auth_enabled': self.auth_config.enabled
            }
        }
        
        return web.json_response(status)
    
    async def api_stats(self, request: web.Request) -> web.Response:
        """API: Получение статистики"""
        stats = await self.node_manager.get_stats()
        return web.json_response(stats)
    
    async def api_get_coins(self, request: web.Request) -> web.Response:
        """API: Получение списка монет"""
        coins = self.node_manager.get_enabled_coins()
        
        coin_details = []
        for coin in coins:
            try:
                config = NodeConfig.get_coin_config(coin, self.node_manager.config)
                coin_details.append({
                    'symbol': coin,
                    'name': config.get('coin_name', coin),
                    'enabled': config.get('enabled', True),
                    'network': config.get('network', 'mainnet'),
                    'master_address': config.get('master_address', ''),
                    'min_collection_amount': config.get('min_collection_amount', 0.001)
                })
            except Exception as e:
                logger.error(f"Error getting config for {coin}: {e}")
        
        return web.json_response(coin_details)
    
    async def api_get_nodes(self, request: web.Request) -> web.Response:
        """API: Получение информации о всех нодах"""
        nodes_info = []
        
        for coin in self.node_manager.get_enabled_coins():
            try:
                node = await self.node_manager.get_node(coin)
                info = await node.get_blockchain_info()
                
                node_info = {
                    'coin': coin,
                    'connected': node.is_connected(),
                    'block_height': info.get('blocks', 0),
                    'network': info.get('chain', 'unknown'),
                    'difficulty': info.get('difficulty', 0),
                    'size_on_disk': info.get('size_on_disk', 0)
                }
                
                nodes_info.append(node_info)
            except Exception as e:
                logger.error(f"Error getting info for {coin}: {e}")
                nodes_info.append({
                    'coin': coin,
                    'connected': False,
                    'error': str(e)
                })
        
        return web.json_response(nodes_info)
    
    async def api_connect_node(self, request: web.Request) -> web.Response:
        """API: Подключение к ноде"""
        coin = request.match_info.get('coin').upper()
        
        try:
            node = await self.node_manager.get_node(coin)
            connected = await node.connect()
            
            return web.json_response({
                'success': connected,
                'coin': coin,
                'message': f"Node {coin} {'connected' if connected else 'failed to connect'}"
            })
        except Exception as e:
            logger.error(f"Error connecting node {coin}: {e}")
            return web.json_response({
                'success': False,
                'coin': coin,
                'error': str(e)
            }, status=500)
    
    async def api_disconnect_node(self, request: web.Request) -> web.Response:
        """API: Отключение от ноды"""
        coin = request.match_info.get('coin').upper()
        
        try:
            if coin in self.node_manager._nodes:
                node = self.node_manager._nodes[coin]
                disconnected = await node.disconnect()
                
                # Удаляем из кэша
                if disconnected:
                    del self.node_manager._nodes[coin]
                
                return web.json_response({
                    'success': disconnected,
                    'coin': coin,
                    'message': f"Node {coin} disconnected"
                })
            else:
                return web.json_response({
                    'success': False,
                    'coin': coin,
                    'error': f"Node {coin} not found"
                }, status=404)
        except Exception as e:
            logger.error(f"Error disconnecting node {coin}: {e}")
            return web.json_response({
                'success': False,
                'coin': coin,
                'error': str(e)
            }, status=500)
    
    async def api_get_node_info(self, request: web.Request) -> web.Response:
        """API: Получение информации о ноде"""
        coin = request.match_info.get('coin').upper()
        
        try:
            node = await self.node_manager.get_node(coin)
            info = await node.get_blockchain_info()
            
            return web.json_response({
                'coin': coin,
                'connected': node.is_connected(),
                'info': info
            })
        except Exception as e:
            logger.error(f"Error getting node info for {coin}: {e}")
            return web.json_response({
                'coin': coin,
                'connected': False,
                'error': str(e)
            }, status=500)
    
    async def api_get_balance(self, request: web.Request) -> web.Response:
        """API: Получение баланса адреса"""
        coin = request.match_info.get('coin').upper()
        address = request.match_info.get('address')
        
        try:
            node = await self.node_manager.get_node(coin)
            balance = await node.get_balance(address)
            
            return web.json_response({
                'coin': coin,
                'address': address,
                'balance': balance
            })
        except Exception as e:
            logger.error(f"Error getting balance for {coin}:{address}: {e}")
            return web.json_response({
                'error': str(e),
                'coin': coin,
                'address': address
            }, status=500)
    
    async def api_get_transactions(self, request: web.Request) -> web.Response:
        """API: Получение транзакций адреса"""
        coin = request.match_info.get('coin').upper()
        address = request.match_info.get('address')
        limit = int(request.query.get('limit', 10))
        
        try:
            node = await self.node_manager.get_node(coin)
            history = await node.get_transaction_history(address, limit)
            
            return web.json_response({
                'coin': coin,
                'address': address,
                'transactions': history,
                'count': len(history)
            })
        except Exception as e:
            logger.error(f"Error getting transactions for {coin}:{address}: {e}")
            return web.json_response({
                'error': str(e),
                'coin': coin,
                'address': address
            }, status=500)
    
    async def api_get_utxos(self, request: web.Request) -> web.Response:
        """API: Получение UTXO адреса"""
        coin = request.match_info.get('coin').upper()
        address = request.match_info.get('address')
        
        try:
            node = await self.node_manager.get_node(coin)
            utxos = await node.get_address_utxos(address)
            
            return web.json_response({
                'coin': coin,
                'address': address,
                'utxos': utxos,
                'count': len(utxos),
                'total': sum(u.get('amount', 0) for u in utxos)
            })
        except Exception as e:
            logger.error(f"Error getting UTXOs for {coin}:{address}: {e}")
            return web.json_response({
                'error': str(e),
                'coin': coin,
                'address': address
            }, status=500)
    
    async def api_start_monitoring(self, request: web.Request) -> web.Response:
        """API: Запуск мониторинга"""
        try:
            data = await request.json()
            coin = data.get('coin')
            
            if coin:
                await self.node_manager.start_monitoring(coin)
                message = f"Monitoring started for {coin}"
            else:
                await self.node_manager.start_monitoring_for_all()
                message = "Monitoring started for all coins"
            
            return web.json_response({
                'success': True,
                'message': message
            })
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def api_stop_monitoring(self, request: web.Request) -> web.Response:
        """API: Остановка мониторинга"""
        try:
            data = await request.json()
            coin = data.get('coin')
            
            if coin and coin in self.node_manager._monitors:
                await self.node_manager._monitors[coin].stop()
                del self.node_manager._monitors[coin]
                message = f"Monitoring stopped for {coin}"
            else:
                # Останавливаем все мониторы
                for monitor in self.node_manager._monitors.values():
                    await monitor.stop()
                self.node_manager._monitors.clear()
                message = "Monitoring stopped for all coins"
            
            return web.json_response({
                'success': True,
                'message': message
            })
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def api_monitor_address(self, request: web.Request) -> web.Response:
        """API: Добавление адреса в мониторинг"""
        try:
            data = await request.json()
            coin = data.get('coin')
            address = data.get('address')
            
            if not coin or not address:
                return web.json_response({
                    'success': False,
                    'error': 'Missing coin or address'
                }, status=400)
            
            await self.node_manager.monitor_address(coin, address)
            
            return web.json_response({
                'success': True,
                'message': f"Address {address} added to monitoring for {coin}"
            })
        except Exception as e:
            logger.error(f"Error adding address to monitoring: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def api_unmonitor_address(self, request: web.Request) -> web.Response:
        """API: Удаление адреса из мониторинга"""
        try:
            data = await request.json()
            coin = data.get('coin')
            address = data.get('address')
            
            if not coin or not address:
                return web.json_response({
                    'success': False,
                    'error': 'Missing coin or address'
                }, status=400)
            
            await self.node_manager.unmonitor_address(coin, address)
            
            return web.json_response({
                'success': True,
                'message': f"Address {address} removed from monitoring for {coin}"
            })
        except Exception as e:
            logger.error(f"Error removing address from monitoring: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def api_collect_funds(self, request: web.Request) -> web.Response:
        """API: Сбор средств"""
        try:
            data = await request.json()
            coin = data.get('coin')
            address = data.get('address')
            private_key = data.get('private_key')  # Осторожно!
            
            if not coin or not address:
                return web.json_response({
                    'success': False,
                    'error': 'Missing coin or address'
                }, status=400)
            
            collector = await self.node_manager.create_collector(coin)
            result = await collector.collect_from_address(address, private_key)
            
            return web.json_response({
                'success': result.get('success', False),
                'result': result
            })
        except Exception as e:
            logger.error(f"Error collecting funds: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def api_estimate_collection(self, request: web.Request) -> web.Response:
        """API: Оценка сбора средств"""
        try:
            data = await request.json()
            coin = data.get('coin')
            address = data.get('address')
            
            if not coin or not address:
                return web.json_response({
                    'success': False,
                    'error': 'Missing coin or address'
                }, status=400)
            
            collector = await self.node_manager.create_collector(coin)
            estimation = await collector.estimate_collection(address)
            
            return web.json_response({
                'success': True,
                'estimation': estimation
            })
        except Exception as e:
            logger.error(f"Error estimating collection: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def api_collection_status(self, request: web.Request) -> web.Response:
        """API: Статус сбора средств"""
        return web.json_response({
            'running': self.node_manager._is_running,
            'collectors': list(self.node_manager._collectors.keys())
        })
    
    async def api_get_config(self, request: web.Request) -> web.Response:
        """API: Получение конфигурации"""
        # Возвращаем только безопасные части конфигурации
        safe_config = self.node_manager.config.copy()
        
        # Удаляем чувствительные данные
        sensitive_keys = ['api_key', 'private_key', 'password', 'secret']
        for key in sensitive_keys:
            if key in safe_config.get('nownodes', {}):
                safe_config['nownodes'][key] = '***'
        
        for coin, coin_config in safe_config.get('coins', {}).items():
            if 'master_address' in coin_config:
                addr = coin_config['master_address']
                if addr and len(addr) > 10:
                    coin_config['master_address'] = f"{addr[:10]}...{addr[-5:]}"
        
        return web.json_response(safe_config)
    
    async def api_update_config(self, request: web.Request) -> web.Response:
        """API: Обновление конфигурации"""
        try:
            data = await request.json()
            
            # Обновляем только разрешенные поля
            allowed_keys = ['services', 'database', 'web_server', 'auth']
            
            for key in allowed_keys:
                if key in data:
                    if key not in self.node_manager.config:
                        self.node_manager.config[key] = {}
                    self.node_manager.config[key].update(data[key])
            
            return web.json_response({
                'success': True,
                'message': 'Configuration updated'
            })
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def api_reload_config(self, request: web.Request) -> web.Response:
        """API: Перезагрузка конфигурации"""
        try:
            # Перезагружаем конфигурацию из файла
            self.node_manager.config = NodeConfig.load_config()
            
            return web.json_response({
                'success': True,
                'message': 'Configuration reloaded from file'
            })
        except Exception as e:
            logger.error(f"Error reloading config: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def api_save_config(self, request: web.Request) -> web.Response:
        """API: Сохранение конфигурации в файл"""
        try:
            NodeConfig.save_config(self.node_manager.config)
            
            return web.json_response({
                'success': True,
                'message': 'Configuration saved to file'
            })
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def api_get_logs(self, request: web.Request) -> web.Response:
        """API: Получение логов"""
        try:
            lines = int(request.query.get('lines', 100))
            level = request.query.get('level', 'INFO')
            
            # Чтение логов из файла если настроено файловое логирование
            log_file = None
            for handler in logging.getLogger().handlers:
                if isinstance(handler, logging.FileHandler):
                    log_file = handler.baseFilename
                    break
            
            logs = []
            if log_file and os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines_content = f.readlines()[-lines:]
                    logs = [line.strip() for line in lines_content]
            else:
                # Возвращаем последние логи из памяти
                logs = ["File logging not configured"]
            
            return web.json_response({
                'logs': logs,
                'count': len(logs),
                'source': log_file or 'memory'
            })
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return web.json_response({
                'error': str(e)
            }, status=500)
    
    async def api_stream_logs(self, request: web.Request) -> web.Response:
        """API: Потоковая передача логов (Server-Sent Events)"""
        response = web.StreamResponse()
        response.headers['Content-Type'] = 'text/event-stream'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'
        
        await response.prepare(request)
        
        try:
            # Создаем канал для новых логов
            log_queue = asyncio.Queue()
            
            # Создаем обработчик логов
            class LogHandler(logging.Handler):
                def emit(self, record):
                    log_entry = self.format(record)
                    asyncio.create_task(log_queue.put(log_entry))
            
            handler = LogHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logging.getLogger().addHandler(handler)
            
            while True:
                try:
                    log_entry = await asyncio.wait_for(log_queue.get(), timeout=30)
                    await response.write(f"data: {json.dumps({'log': log_entry})}\n\n".encode())
                except asyncio.TimeoutError:
                    # Отправляем keep-alive
                    await response.write(b': keep-alive\n\n')
                
                # Проверяем закрыто ли соединение
                if request.transport.is_closing():
                    break
            
            # Убираем обработчик
            logging.getLogger().removeHandler(handler)
            
        except Exception as e:
            logger.error(f"Error in log stream: {e}")
        finally:
            await response.write_eof()
        
        return response
    
    async def api_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """API: WebSocket для реального времени"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        logger.info(f"WebSocket connected from {request.remote}")
        
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    action = data.get('action')
                    
                    if action == 'subscribe':
                        # Подписка на события
                        channel = data.get('channel')
                        await self._handle_websocket_subscription(ws, channel)
                    
                    elif action == 'unsubscribe':
                        # Отписка от событий
                        channel = data.get('channel')
                        await self._handle_websocket_unsubscription(ws, channel)
                    
                    elif action == 'ping':
                        # Ответ на ping
                        await ws.send_str(json.dumps({'action': 'pong'}))
                    
                    else:
                        await ws.send_str(json.dumps({
                            'error': f'Unknown action: {action}'
                        }))
                
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
        
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            logger.info(f"WebSocket disconnected from {request.remote}")
        
        return ws
    
    async def _handle_websocket_subscription(self, ws, channel):
        """Обработка подписки на WebSocket канал"""
        if channel == 'blocks':
            # Подписка на новые блоки
            pass
        elif channel == 'transactions':
            # Подписка на транзакции
            pass
        elif channel == 'status':
            # Подписка на изменение статуса
            pass
        
        await ws.send_str(json.dumps({
            'action': 'subscribed',
            'channel': channel,
            'timestamp': datetime.now().isoformat()
        }))
    
    async def _handle_websocket_unsubscription(self, ws, channel):
        """Обработка отписки от WebSocket канала"""
        await ws.send_str(json.dumps({
            'action': 'unsubscribed',
            'channel': channel,
            'timestamp': datetime.now().isoformat()
        }))
    
    async def api_restart(self, request: web.Request) -> web.Response:
        """API: Перезапуск системы"""
        # Этот метод должен быть доступен только администраторам
        return web.json_response({
            'success': True,
            'message': 'Restart initiated (placeholder)'
        })
    
    async def api_shutdown(self, request: web.Request) -> web.Response:
        """API: Выключение системы"""
        # Этот метод должен быть доступен только администраторам
        return web.json_response({
            'success': True,
            'message': 'Shutdown initiated (placeholder)'
        })
    
    async def api_system_info(self, request: web.Request) -> web.Response:
        """API: Получение системной информации"""
        try:
            # Использование памяти
            memory = psutil.virtual_memory()
            
            # Использование CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Дисковое пространство
            disk = psutil.disk_usage('/')
            
            # Сетевая активность
            net_io = psutil.net_io_counters()
            
            # Информация о системе
            system_info = {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'python_version': platform.python_version(),
                'hostname': platform.node(),
                'processor': platform.processor(),
                'uptime': str(datetime.now() - self.start_time),
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'cpu': {
                    'percent': cpu_percent,
                    'cores': psutil.cpu_count(),
                    'physical_cores': psutil.cpu_count(logical=False)
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            }
            
            return web.json_response(system_info)
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return web.json_response({
                'error': str(e)
            }, status=500)
    
    # Веб-интерфейс методы
    async def web_index(self, request: web.Request) -> web.Response:
        """Веб: Главная страница"""
        return web.HTTPFound('/dashboard')
    
    async def web_dashboard(self, request: web.Request) -> web.Response:
        """Веб: Панель управления"""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Node Manager - Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .header {
                    background: #2c3e50;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }
                .stat-card {
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .stat-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                }
                .stat-label {
                    color: #7f8c8d;
                    font-size: 14px;
                }
                .nav {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                    flex-wrap: wrap;
                }
                .nav a {
                    background: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    text-decoration: none;
                    color: #2c3e50;
                    border: 1px solid #ddd;
                }
                .nav a:hover {
                    background: #f0f0f0;
                }
                .node-list {
                    background: white;
                    border-radius: 5px;
                    padding: 20px;
                    margin-top: 20px;
                }
                .node-item {
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .status-connected { color: #27ae60; }
                .status-disconnected { color: #e74c3c; }
                .status-syncing { color: #f39c12; }
                .logout-btn {
                    background: #e74c3c;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-left: auto;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h1>Node Manager Dashboard</h1>
                        <p>Control panel for cryptocurrency nodes</p>
                    </div>
                    <button class="logout-btn" onclick="logout()">Logout</button>
                </div>
            </div>
            
            <div class="nav">
                <a href="/dashboard">Dashboard</a>
                <a href="/nodes">Nodes</a>
                <a href="/monitoring">Monitoring</a>
                <a href="/collection">Collection</a>
                <a href="/config">Configuration</a>
                <a href="/logs">Logs</a>
            </div>
            
            <div class="stats-grid" id="stats">
                <!-- Статистика будет загружена через JavaScript -->
            </div>
            
            <div class="node-list">
                <h3>Active Nodes</h3>
                <div id="nodesList">
                    <!-- Список нод будет загружен через JavaScript -->
                </div>
            </div>
            
            <div class="stat-card">
                <h3>System Information</h3>
                <div id="systemInfo">
                    <!-- Системная информация будет загружена через JavaScript -->
                </div>
            </div>
            
            <script>
                let token = localStorage.getItem('token');
                
                async function checkAuth() {
                    if (!token) {
                        window.location.href = '/login';
                        return false;
                    }
                    
                    try {
                        const response = await fetch('/api/v1/auth/check', {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        
                        if (!response.ok) {
                            window.location.href = '/login';
                            return false;
                        }
                        
                        return true;
                    } catch (error) {
                        window.location.href = '/login';
                        return false;
                    }
                }
                
                async function loadStats() {
                    if (!await checkAuth()) return;
                    
                    try {
                        const response = await fetch('/api/v1/status', {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        const data = await response.json();
                        
                        const statsContainer = document.getElementById('stats');
                        statsContainer.innerHTML = `
                            <div class="stat-card">
                                <div class="stat-value">${data.manager.connected ? '✅' : '❌'}</div>
                                <div class="stat-label">Manager Status</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${data.enabled_coins.length}</div>
                                <div class="stat-label">Enabled Coins</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${data.manager.monitoring ? '✅' : '❌'}</div>
                                <div class="stat-label">Monitoring</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value">${data.manager.collection ? '✅' : '❌'}</div>
                                <div class="stat-label">Auto Collection</div>
                            </div>
                        `;
                        
                        // Загружаем список нод
                        loadNodes(data.nodes);
                        
                        // Загружаем системную информацию
                        loadSystemInfo();
                        
                    } catch (error) {
                        console.error('Error loading stats:', error);
                    }
                }
                
                async function loadNodes(nodes) {
                    const nodesList = document.getElementById('nodesList');
                    if (!nodesList) return;
                    
                    let html = '';
                    for (const [coin, info] of Object.entries(nodes)) {
                        const statusClass = info.connected ? 'status-connected' : 'status-disconnected';
                        const statusText = info.connected ? 'Connected' : 'Disconnected';
                        
                        html += `
                            <div class="node-item">
                                <div>
                                    <strong>${coin}</strong>
                                    <span class="${statusClass}">${statusText}</span>
                                </div>
                                <div>
                                    ${info.block_height ? `Block: ${info.block_height}` : ''}
                                    ${info.network ? ` | Network: ${info.network}` : ''}
                                </div>
                                <div>
                                    <button onclick="connectNode('${coin}')">Connect</button>
                                    <button onclick="disconnectNode('${coin}')">Disconnect</button>
                                </div>
                            </div>
                        `;
                    }
                    
                    nodesList.innerHTML = html || '<p>No nodes available</p>';
                }
                
                async function loadSystemInfo() {
                    try {
                        const response = await fetch('/api/v1/system/info', {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        const data = await response.json();
                        
                        const systemInfo = document.getElementById('systemInfo');
                        if (systemInfo) {
                            systemInfo.innerHTML = `
                                <p><strong>Platform:</strong> ${data.platform} ${data.platform_version}</p>
                                <p><strong>Python:</strong> ${data.python_version}</p>
                                <p><strong>Hostname:</strong> ${data.hostname}</p>
                                <p><strong>Uptime:</strong> ${data.uptime}</p>
                                <p><strong>CPU:</strong> ${data.cpu.percent}% (${data.cpu.cores} cores)</p>
                                <p><strong>Memory:</strong> ${(data.memory.used / 1024 / 1024 / 1024).toFixed(2)} GB / ${(data.memory.total / 1024 / 1024 / 1024).toFixed(2)} GB (${data.memory.percent}%)</p>
                            `;
                        }
                    } catch (error) {
                        console.error('Error loading system info:', error);
                    }
                }
                
                async function connectNode(coin) {
                    try {
                        const response = await fetch(`/api/v1/nodes/${coin}/connect`, {
                            method: 'POST',
                            headers: { 
                                'Authorization': `Bearer ${token}`,
                                'Content-Type': 'application/json'
                            }
                        });
                        const result = await response.json();
                        alert(result.message);
                        loadStats();
                    } catch (error) {
                        console.error('Error connecting node:', error);
                        alert('Error connecting node');
                    }
                }
                
                async function disconnectNode(coin) {
                    try {
                        const response = await fetch(`/api/v1/nodes/${coin}/disconnect`, {
                            method: 'POST',
                            headers: { 
                                'Authorization': `Bearer ${token}`,
                                'Content-Type': 'application/json'
                            }
                        });
                        const result = await response.json();
                        alert(result.message);
                        loadStats();
                    } catch (error) {
                        console.error('Error disconnecting node:', error);
                        alert('Error disconnecting node');
                    }
                }
                
                async function logout() {
                    try {
                        await fetch('/api/v1/auth/logout', {
                            method: 'POST',
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                    } catch (error) {
                        // Ignore errors
                    }
                    
                    localStorage.removeItem('token');
                    document.cookie = 'session_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                    window.location.href = '/login';
                }
                
                // Загружаем статистику при загрузке страницы
                document.addEventListener('DOMContentLoaded', () => {
                    loadStats();
                    
                    // Обновляем каждые 10 секунд
                    setInterval(loadStats, 10000);
                });
            </script>
        </body>
        </html>
        """
        
        return web.Response(text=html, content_type='text/html')
    
    async def web_nodes(self, request: web.Request) -> web.Response:
        """Веб: Управление нодами"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Node Manager - Nodes</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .header {
                    background: #2c3e50;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background: white;
                    border-radius: 5px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                    font-weight: bold;
                }
                .status-connected { color: #27ae60; }
                .status-disconnected { color: #e74c3c; }
                button {
                    padding: 5px 10px;
                    margin: 2px;
                    border: none;
                    border-radius: 3px;
                    cursor: pointer;
                }
                .connect-btn { background: #27ae60; color: white; }
                .disconnect-btn { background: #e74c3c; color: white; }
                .info-btn { background: #3498db; color: white; }
                .nav {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                    flex-wrap: wrap;
                }
                .nav a {
                    background: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    text-decoration: none;
                    color: #2c3e50;
                    border: 1px solid #ddd;
                }
                .nav a:hover {
                    background: #f0f0f0;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Node Management</h1>
            </div>
            
            <div class="nav">
                <a href="/dashboard">← Back to Dashboard</a>
                <a href="/nodes">Nodes</a>
                <a href="/monitoring">Monitoring</a>
                <a href="/collection">Collection</a>
                <a href="/config">Configuration</a>
                <a href="/logs">Logs</a>
            </div>
            
            <table id="nodesTable">
                <thead>
                    <tr>
                        <th>Coin</th>
                        <th>Status</th>
                        <th>Block Height</th>
                        <th>Network</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Данные будут загружены через JavaScript -->
                </tbody>
            </table>
            
            <script>
                let token = localStorage.getItem('token');
                
                async function loadNodes() {
                    if (!token) {
                        window.location.href = '/login';
                        return;
                    }
                    
                    try {
                        const response = await fetch('/api/v1/nodes', {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        
                        if (!response.ok) {
                            if (response.status === 401) {
                                window.location.href = '/login';
                                return;
                            }
                            throw new Error('Failed to load nodes');
                        }
                        
                        const nodes = await response.json();
                        
                        const tbody = document.querySelector('#nodesTable tbody');
                        tbody.innerHTML = '';
                        
                        nodes.forEach(node => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td><strong>${node.coin}</strong></td>
                                <td class="${node.connected ? 'status-connected' : 'status-disconnected'}">
                                    ${node.connected ? '✅ Connected' : '❌ Disconnected'}
                                </td>
                                <td>${node.block_height || 'N/A'}</td>
                                <td>${node.network || 'Unknown'}</td>
                                <td>
                                    <button class="connect-btn" onclick="connectNode('${node.coin}')">Connect</button>
                                    <button class="disconnect-btn" onclick="disconnectNode('${node.coin}')">Disconnect</button>
                                    <button class="info-btn" onclick="showNodeInfo('${node.coin}')">Info</button>
                                </td>
                            `;
                            tbody.appendChild(row);
                        });
                    } catch (error) {
                        console.error('Error loading nodes:', error);
                        alert('Error loading nodes: ' + error.message);
                    }
                }
                
                async function connectNode(coin) {
                    try {
                        const response = await fetch(`/api/v1/nodes/${coin}/connect`, {
                            method: 'POST',
                            headers: { 
                                'Authorization': `Bearer ${token}`,
                                'Content-Type': 'application/json'
                            }
                        });
                        
                        const result = await response.json();
                        alert(result.message);
                        loadNodes();
                    } catch (error) {
                        console.error('Error connecting node:', error);
                        alert('Error connecting node');
                    }
                }
                
                async function disconnectNode(coin) {
                    try {
                        const response = await fetch(`/api/v1/nodes/${coin}/disconnect`, {
                            method: 'POST',
                            headers: { 
                                'Authorization': `Bearer ${token}`,
                                'Content-Type': 'application/json'
                            }
                        });
                        
                        const result = await response.json();
                        alert(result.message);
                        loadNodes();
                    } catch (error) {
                        console.error('Error disconnecting node:', error);
                        alert('Error disconnecting node');
                    }
                }
                
                async function showNodeInfo(coin) {
                    try {
                        const response = await fetch(`/api/v1/nodes/${coin}/info`, {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        
                        const info = await response.json();
                        alert(JSON.stringify(info, null, 2));
                    } catch (error) {
                        console.error('Error getting node info:', error);
                        alert('Error getting node info');
                    }
                }
                
                // Загружаем ноды при загрузке страницы
                document.addEventListener('DOMContentLoaded', () => {
                    loadNodes();
                    
                    // Обновляем каждые 30 секунд
                    setInterval(loadNodes, 30000);
                });
            </script>
        </body>
        </html>
        """
        
        return web.Response(text=html, content_type='text/html')
    
    async def web_monitoring(self, request: web.Request) -> web.Response:
        """Веб: Мониторинг"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Node Manager - Monitoring</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .header {
                    background: #2c3e50;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                .monitoring-controls {
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .address-form {
                    margin-top: 20px;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 5px;
                }
                input, select, button {
                    padding: 10px;
                    margin: 5px;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                }
                button {
                    background: #3498db;
                    color: white;
                    cursor: pointer;
                    border: none;
                }
                button:hover {
                    background: #2980b9;
                }
                .danger-btn {
                    background: #e74c3c;
                }
                .danger-btn:hover {
                    background: #c0392b;
                }
                .success-btn {
                    background: #27ae60;
                }
                .success-btn:hover {
                    background: #219653;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Transaction Monitoring</h1>
            </div>
            
            <div class="monitoring-controls">
                <h3>Monitoring Controls</h3>
                <button class="success-btn" onclick="startMonitoring()">Start Monitoring All</button>
                <button class="danger-btn" onclick="stopMonitoring()">Stop Monitoring All</button>
                
                <div class="address-form">
                    <h4>Monitor Address</h4>
                    <select id="coinSelect">
                        <option value="LTC">Litecoin (LTC)</option>
                        <option value="DOGE">Dogecoin (DOGE)</option>
                        <option value="BTC">Bitcoin (BTC)</option>
                    </select>
                    <input type="text" id="addressInput" placeholder="Enter address to monitor" style="width: 400px;">
                    <button onclick="addAddress()">Add Address</button>
                    
                    <h4>Monitored Addresses</h4>
                    <div id="monitoredAddresses">
                        <!-- Addresses will be loaded here -->
                    </div>
                </div>
            </div>
            
            <script>
                let token = localStorage.getItem('token');
                
                async function startMonitoring() {
                    try {
                        const response = await fetch('/api/v1/monitoring/start', {
                            method: 'POST',
                            headers: {
                                'Authorization': `Bearer ${token}`,
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({})
                        });
                        
                        const result = await response.json();
                        alert(result.message);
                    } catch (error) {
                        console.error('Error starting monitoring:', error);
                        alert('Error starting monitoring');
                    }
                }
                
                async function stopMonitoring() {
                    try {
                        const response = await fetch('/api/v1/monitoring/stop', {
                            method: 'POST',
                            headers: {
                                'Authorization': `Bearer ${token}`,
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({})
                        });
                        
                        const result = await response.json();
                        alert(result.message);
                    } catch (error) {
                        console.error('Error stopping monitoring:', error);
                        alert('Error stopping monitoring');
                    }
                }
                
                async function addAddress() {
                    const coin = document.getElementById('coinSelect').value;
                    const address = document.getElementById('addressInput').value;
                    
                    if (!address) {
                        alert('Please enter an address');
                        return;
                    }
                    
                    try {
                        const response = await fetch('/api/v1/monitoring/address', {
                            method: 'POST',
                            headers: {
                                'Authorization': `Bearer ${token}`,
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ coin, address })
                        });
                        
                        const result = await response.json();
                        if (result.success) {
                            alert('Address added to monitoring');
                            document.getElementById('addressInput').value = '';
                        } else {
                            alert('Error: ' + result.error);
                        }
                    } catch (error) {
                        console.error('Error adding address:', error);
                        alert('Error adding address to monitoring');
                    }
                }
                
                // Check authentication on page load
                document.addEventListener('DOMContentLoaded', () => {
                    if (!token) {
                        window.location.href = '/login';
                    }
                });
            </script>
        </body>
        </html>
        """
        
        return web.Response(text=html, content_type='text/html')
    
    async def web_collection(self, request: web.Request) -> web.Response:
        """Веб: Сбор средств"""
        return web.Response(text="<h1>Collection Page</h1><p>Funds collection interface will be implemented here.</p>", content_type='text/html')
    
    async def web_config(self, request: web.Request) -> web.Response:
        """Веб: Конфигурация"""
        return web.Response(text="<h1>Configuration Page</h1><p>Configuration interface will be implemented here.</p>", content_type='text/html')
    
    async def web_logs(self, request: web.Request) -> web.Response:
        """Веб: Логи"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Node Manager - Logs</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .header {
                    background: #2c3e50;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                .logs-container {
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .log-entry {
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                    font-family: monospace;
                    font-size: 12px;
                }
                .log-error { color: #e74c3c; }
                .log-warning { color: #f39c12; }
                .log-info { color: #3498db; }
                .log-debug { color: #7f8c8d; }
                .controls {
                    margin-bottom: 20px;
                    display: flex;
                    gap: 10px;
                    align-items: center;
                }
                select, button {
                    padding: 8px 12px;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                }
                button {
                    background: #3498db;
                    color: white;
                    cursor: pointer;
                    border: none;
                }
                button:hover {
                    background: #2980b9;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>System Logs</h1>
            </div>
            
            <div class="controls">
                <select id="logLevel">
                    <option value="ALL">All Levels</option>
                    <option value="ERROR">Error</option>
                    <option value="WARNING">Warning</option>
                    <option value="INFO">Info</option>
                    <option value="DEBUG">Debug</option>
                </select>
                <select id="logLines">
                    <option value="50">50 lines</option>
                    <option value="100" selected>100 lines</option>
                    <option value="200">200 lines</option>
                    <option value="500">500 lines</option>
                </select>
                <button onclick="loadLogs()">Refresh</button>
                <button onclick="clearLogs()">Clear</button>
                <button onclick="startLiveLogs()">Live View</button>
                <button onclick="stopLiveLogs()">Stop Live</button>
            </div>
            
            <div class="logs-container" id="logsContainer">
                <!-- Logs will be loaded here -->
            </div>
            
            <script>
                let token = localStorage.getItem('token');
                let liveLogs = false;
                let eventSource = null;
                
                function getLogLevelClass(level) {
                    switch(level) {
                        case 'ERROR': return 'log-error';
                        case 'WARNING': return 'log-warning';
                        case 'INFO': return 'log-info';
                        case 'DEBUG': return 'log-debug';
                        default: return '';
                    }
                }
                
                async function loadLogs() {
                    if (!token) {
                        window.location.href = '/login';
                        return;
                    }
                    
                    const level = document.getElementById('logLevel').value;
                    const lines = document.getElementById('logLines').value;
                    
                    try {
                        const response = await fetch(`/api/v1/logs?level=${level}&lines=${lines}`, {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        
                        const data = await response.json();
                        displayLogs(data.logs);
                    } catch (error) {
                        console.error('Error loading logs:', error);
                        document.getElementById('logsContainer').innerHTML = '<p>Error loading logs: ' + error.message + '</p>';
                    }
                }
                
                function displayLogs(logs) {
                    const container = document.getElementById('logsContainer');
                    let html = '';
                    
                    logs.forEach(log => {
                        // Extract log level from log entry
                        let level = 'INFO';
                        let logClass = 'log-info';
                        
                        if (log.includes('ERROR')) {
                            level = 'ERROR';
                            logClass = 'log-error';
                        } else if (log.includes('WARNING')) {
                            level = 'WARNING';
                            logClass = 'log-warning';
                        } else if (log.includes('DEBUG')) {
                            level = 'DEBUG';
                            logClass = 'log-debug';
                        }
                        
                        const selectedLevel = document.getElementById('logLevel').value;
                        if (selectedLevel !== 'ALL' && selectedLevel !== level) {
                            return;
                        }
                        
                        html += `<div class="log-entry ${logClass}">${log}</div>`;
                    });
                    
                    container.innerHTML = html || '<p>No logs found</p>';
                    
                    // Scroll to bottom
                    container.scrollTop = container.scrollHeight;
                }
                
                function clearLogs() {
                    document.getElementById('logsContainer').innerHTML = '';
                }
                
                function startLiveLogs() {
                    if (liveLogs) return;
                    
                    liveLogs = true;
                    eventSource = new EventSource('/api/v1/logs/stream');
                    
                    eventSource.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        const container = document.getElementById('logsContainer');
                        const logEntry = document.createElement('div');
                        
                        let logClass = 'log-info';
                        if (data.log.includes('ERROR')) logClass = 'log-error';
                        else if (data.log.includes('WARNING')) logClass = 'log-warning';
                        else if (data.log.includes('DEBUG')) logClass = 'log-debug';
                        
                        logEntry.className = `log-entry ${logClass}`;
                        logEntry.textContent = data.log;
                        
                        const selectedLevel = document.getElementById('logLevel').value;
                        const level = logClass.replace('log-', '').toUpperCase();
                        
                        if (selectedLevel === 'ALL' || selectedLevel === level) {
                            container.appendChild(logEntry);
                            container.scrollTop = container.scrollHeight;
                        }
                    };
                    
                    eventSource.onerror = function(error) {
                        console.error('EventSource error:', error);
                        stopLiveLogs();
                    };
                }
                
                function stopLiveLogs() {
                    if (eventSource) {
                        eventSource.close();
                        eventSource = null;
                    }
                    liveLogs = false;
                }
                
                // Load logs on page load
                document.addEventListener('DOMContentLoaded', () => {
                    loadLogs();
                    
                    // Refresh every 30 seconds if not in live mode
                    setInterval(() => {
                        if (!liveLogs) {
                            loadLogs();
                        }
                    }, 30000);
                });
                
                // Clean up on page unload
                window.addEventListener('beforeunload', () => {
                    stopLiveLogs();
                });
            </script>
        </body>
        </html>
        """
        
        return web.Response(text=html, content_type='text/html')
    
    async def web_login(self, request: web.Request) -> web.Response:
        """Веб: Страница входа"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Node Manager - Login</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                }
                .login-container {
                    background: rgba(255, 255, 255, 0.95);
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    width: 350px;
                    text-align: center;
                }
                h1 {
                    color: #2c3e50;
                    margin-bottom: 30px;
                    font-size: 24px;
                }
                input {
                    width: 100%;
                    padding: 15px;
                    margin: 10px 0;
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    box-sizing: border-box;
                    font-size: 16px;
                    transition: border-color 0.3s;
                }
                input:focus {
                    outline: none;
                    border-color: #3498db;
                }
                button {
                    width: 100%;
                    padding: 15px;
                    background: #3498db;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                    transition: background 0.3s;
                    margin-top: 10px;
                }
                button:hover {
                    background: #2980b9;
                }
                .error {
                    color: #e74c3c;
                    text-align: center;
                    margin-top: 10px;
                    padding: 10px;
                    border-radius: 5px;
                    background: #ffeaea;
                    display: none;
                }
                .logo {
                    font-size: 48px;
                    margin-bottom: 20px;
                    color: #3498db;
                }
                .demo-info {
                    margin-top: 20px;
                    padding: 10px;
                    background: #f8f9fa;
                    border-radius: 5px;
                    font-size: 12px;
                    color: #7f8c8d;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <div class="logo">🔗</div>
                <h1>Node Manager</h1>
                <p style="color: #7f8c8d; margin-bottom: 30px;">Sign in to manage your cryptocurrency nodes</p>
                
                <form id="loginForm">
                    <input type="text" id="username" placeholder="Username" required autocomplete="username">
                    <input type="password" id="password" placeholder="Password" required autocomplete="current-password">
                    <button type="submit">Login</button>
                </form>
                
                <div class="error" id="errorMessage"></div>
                
                <div class="demo-info">
                    <p><strong>Default credentials:</strong><br>
                    Username: admin<br>
                    Password: (set in .env file or config)</p>
                </div>
            </div>
            
            <script>
                document.getElementById('loginForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const username = document.getElementById('username').value;
                    const password = document.getElementById('password').value;
                    const errorElement = document.getElementById('errorMessage');
                    
                    // Clear previous errors
                    errorElement.style.display = 'none';
                    errorElement.textContent = '';
                    
                    // Show loading state
                    const submitBtn = document.querySelector('button[type="submit"]');
                    const originalText = submitBtn.textContent;
                    submitBtn.textContent = 'Logging in...';
                    submitBtn.disabled = true;
                    
                    try {
                        const response = await fetch('/api/v1/auth/login', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ username, password })
                        });
                        
                        if (response.ok) {
                            const data = await response.json();
                            
                            // Save token to localStorage for API calls
                            localStorage.setItem('token', data.token);
                            
                            // Successful login, redirect to dashboard
                            window.location.href = '/';
                        } else {
                            const data = await response.json();
                            errorElement.textContent = data.error || 'Login failed';
                            errorElement.style.display = 'block';
                            
                            // Shake animation for error
                            errorElement.style.animation = 'none';
                            setTimeout(() => {
                                errorElement.style.animation = 'shake 0.5s';
                            }, 10);
                        }
                    } catch (error) {
                        errorElement.textContent = 'Network error. Please check your connection.';
                        errorElement.style.display = 'block';
                    } finally {
                        // Restore button state
                        submitBtn.textContent = originalText;
                        submitBtn.disabled = false;
                    }
                });
                
                // Add shake animation
                const style = document.createElement('style');
                style.textContent = `
                    @keyframes shake {
                        0%, 100% { transform: translateX(0); }
                        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                        20%, 40%, 60%, 80% { transform: translateX(5px); }
                    }
                `;
                document.head.appendChild(style);
                
                // Focus on username field
                document.getElementById('username').focus();
                
                // Handle Enter key
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.target.matches('button')) {
                        document.getElementById('loginForm').requestSubmit();
                    }
                });
            </script>
        </body>
        </html>
        """
        
        return web.Response(text=html, content_type='text/html')
    
    async def web_logout(self, request: web.Request) -> web.Response:
        """Веб: Выход из системы"""
        # Удаляем сессию
        session_id = request.cookies.get('session_id')
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        # Редирект на страницу логина
        response = web.HTTPFound('/login')
        response.del_cookie('session_id')
        return response
    
    # Вспомогательные методы
    def _hash_password(self, password: str) -> str:
        """Хэширование пароля"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    def _check_password(self, password: str, password_hash: str) -> bool:
        """Проверка пароля"""
        try:
            return bcrypt.checkpw(password.encode(), password_hash.encode())
        except:
            return False
    
    def _check_credentials(self, username: str, password: str) -> bool:
        """Проверка учетных данных"""
        if not self.auth_config.enabled:
            return True  # Аутентификация отключена
        
        if username != self.auth_config.admin_username:
            return False
        
        if not self.auth_config.admin_password_hash:
            # Если хэш не установлен, создаем его из пароля
            self.auth_config.admin_password_hash = self._hash_password(password)
            return True
        
        return self._check_password(password, self.auth_config.admin_password_hash)
    
    def _create_jwt(self, username: str) -> str:
        """Создание JWT токена"""
        payload = {
            'username': username,
            'role': 'admin',
            'exp': datetime.now() + timedelta(seconds=self.config.session_timeout)
        }
        
        return jwt.encode(
            payload,
            self.auth_config.jwt_secret,
            algorithm=self.auth_config.jwt_algorithm
        )
    
    def _verify_jwt(self, token: str) -> bool:
        """Проверка JWT токена"""
        try:
            jwt.decode(
                token,
                self.auth_config.jwt_secret,
                algorithms=[self.auth_config.jwt_algorithm]
            )
            return True
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return False
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return False
        except Exception as e:
            logger.error(f"JWT verification error: {e}")
            return False
    
    def _decode_jwt(self, token: str) -> dict:
        """Декодирование JWT токена"""
        try:
            return jwt.decode(
                token,
                self.auth_config.jwt_secret,
                algorithms=[self.auth_config.jwt_algorithm]
            )
        except:
            return {}
    
    # Управление сервером
    async def start(self):
        """Запуск веб-сервера"""
        self.start_time = datetime.now()
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = web.TCPSite(
            self.runner,
            self.config.host,
            self.config.port
        )
        
        await self.site.start()
        
        logger.info(f"Web server started on http://{self.config.host}:{self.config.port}")
        logger.info(f"API available at http://{self.config.host}:{self.config.port}{self.config.api_prefix}")
        logger.info(f"Web UI available at http://{self.config.host}:{self.config.port}")
        
        if self.auth_config.enabled:
            logger.info(f"Authentication enabled. Username: {self.auth_config.admin_username}")
            if not self.auth_config.admin_password_hash:
                logger.warning("Admin password not set! Please set NODE_MANAGER_ADMIN_PASSWORD")
        else:
            logger.warning("Authentication is disabled!")
    
    async def stop(self):
        """Остановка веб-сервера"""
        if self.site:
            await self.site.stop()
            self.site = None
        
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
        
        logger.info("Web server stopped")
    
    async def restart(self):
        """Перезапуск веб-сервера"""
        logger.info("Restarting web server...")
        await self.stop()
        await self.start()


# Упрощенный запуск
async def start_web_server(node_manager: NodeManager = None, config: Dict[str, Any] = None):
    """
    Запуск веб-сервера
    
    Args:
        node_manager: Экземпляр NodeManager (если None, создается новый)
        config: Конфигурация веб-сервера
    
    Returns:
        WebServer: Экземпляр веб-сервера
    """
    if node_manager is None:
        node_manager = await create_node_manager(auto_start=True)
    
    server = WebServer(node_manager, config)
    await server.start()
    
    return server


# CLI команда для запуска веб-сервера
def web_server_cli():
    """CLI для запуска веб-сервера"""
    import argparse
    import getpass
    
    parser = argparse.ArgumentParser(description='Node Manager Web Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--no-auth', action='store_true', help='Disable authentication')
    parser.add_argument('--username', default='admin', help='Admin username')
    parser.add_argument('--password', help='Admin password (if not set, will be prompted)')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--no-web-ui', action='store_true', help='Disable web UI')
    parser.add_argument('--no-api', action='store_true', help='Disable API')
    
    args = parser.parse_args()
    
    # Запрос пароля если не указан и аутентификация включена
    if not args.password and not args.no_auth:
        args.password = getpass.getpass(f'Password for {args.username}: ')
    
    # Конфигурация
    config = {
        'host': args.host,
        'port': args.port,
        'auth_enabled': not args.no_auth,
        'admin_username': args.username,
        'admin_password': args.password,
        'enable_web_ui': not args.no_web_ui,
        'enable_api': not args.no_api
    }
    
    print(f"\n🚀 Starting Node Manager Web Server...")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Authentication: {'Enabled' if not args.no_auth else 'Disabled'}")
    print(f"   Web UI: {'Enabled' if not args.no_web_ui else 'Disabled'}")
    print(f"   API: {'Enabled' if not args.no_api else 'Disabled'}")
    
    if not args.no_auth and args.password:
        print(f"   Username: {args.username}")
        print(f"   Password: {'*' * len(args.password)}")
    
    print(f"\n📡 Web Interface: http://{args.host}:{args.port}")
    print(f"🔌 API Endpoint: http://{args.host}:{args.port}/api/v1")
    print(f"\nPress Ctrl+C to stop the server.\n")
    
    # Запуск
    try:
        loop = asyncio.get_event_loop()
        server_task = loop.create_task(start_web_server(config=config))
        loop.run_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down web server...")
        
        # Остановка сервера
        try:
            loop.run_until_complete(server_task)
        except:
            pass
        
        print("✅ Web server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    web_server_cli()
