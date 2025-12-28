# Node Manager - Универсальный менеджер криптовалютных нод

## 🌟 Возможности

### ✅ Полная поддержка Nownodes
- Единый API ключ для всех монет
- Автоматическое подключение к Blockbook и RPC API
- WebSocket для реального мониторинга
- Поддержка Litecoin (LTC), Dogecoin (DOGE), Bitcoin (BTC)
- Легко добавить любую другую монету

### ✅ Веб-панель управления
- Современный веб-интерфейс с аутентификацией
- Live-мониторинг транзакций и блоков
- Управление нодами через браузер
- Настройка конфигурации онлайн
- Графики и статистика в реальном времени
- Поддержка мобильных устройств
- REST API для интеграции

### ✅ Автоматизация
- Автоматический мониторинг транзакций
- Автоматический сбор средств на мастер-адрес
- Периодическая проверка балансов
- Отписка от адресов после сбора

### ✅ Безопасность
- Централизованное управление ключами
- Валидация всех адресов
- Безопасное хранение конфигурации
- Поддержка переменных окружения
- JWT аутентификация для API
- Rate limiting и CORS

### ✅ Простота использования
- Установка одной командой
- Конфигурация через YAML/JSON
- Готовые примеры ботов
- Подробная документация
- CLI интерфейс

## 🚀 Быстрый старт

### Установка за 30 секунд:

```bash
# Установите модуль
pip install git+https://github.com/glebkoxan36/node-manager.git

# Создайте конфигурацию
node-manager init

# Запустите веб-панель
node-manager-web --username admin
Минимальный рабочий бот:
python
import asyncio
from node_manager import NodeManager

async def main():
    # Инициализация с единым API ключом
    manager = NodeManager()
    
    # Получение ноды Litecoin
    ltc_node = await manager.get_node("LTC")
    
    # Проверка баланса
    balance = await ltc_node.get_balance("ltc1q...")
    print(f"Баланс: {balance['total']} LTC")
    
    # Мониторинг адреса
    await manager.monitor_address("LTC", "ltc1q...")
    
    # Запуск автоматического сбора
    await manager.start_auto_collection()

asyncio.run(main())
Веб-панель управления:
bash
# Запуск веб-панели
node-manager-web --host 0.0.0.0 --port 8080 --username admin

# Доступ по адресу:
# http://ваш-ip-адрес:8080
📦 Установка
Способ 1: Из GitHub (рекомендуется)
bash
# Последняя версия из main ветки
pip install git+https://github.com/glebkoxan36/node-manager.git
Способ 2: Установка для разработки
bash
# Клонируйте репозиторий
git clone https://github.com/glebkoxan36/node-manager.git
cd node-manager

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите в режиме разработки
pip install -e .
Зависимости
Модуль автоматически установит:

aiohttp>=3.8.0 - Асинхронные HTTP запросы

websockets>=11.0.0 - WebSocket клиент

PyYAML>=6.0 - Работа с YAML конфигурацией

python-dotenv>=1.0.0 - Переменные окружения

bip-utils>=2.7.0 - Валидация адресов

aiogram>=2.25.0 - Telegram бот (опционально)

bcrypt>=4.0.0 - Шифрование паролей

pyjwt>=2.0.0 - JWT токены

psutil>=5.9.0 - Мониторинг системы

aiohttp_cors>=0.7.0 - CORS поддержка

🌐 Веб-панель управления
Быстрый запуск веб-панели:
bash
# Запуск с аутентификацией
node-manager-web --username admin --password ваш_пароль

# Запуск без аутентификации (только для тестов)
node-manager-web --no-auth

# Запуск с кастомными настройками
node-manager-web --host 192.168.1.100 --port 9090 --username admin
Доступ к веб-панели:
Откройте браузер: http://ваш-ip-адрес:8080

Войдите с логином/паролем (по умолчанию: admin/admin)

Управляйте всеми нодами через удобный интерфейс

Возможности веб-панели:
📊 Дашборд - Обзор статуса всех нод, графики, статистика

🔌 Управление нодами - Подключение/отключение, информация о блокчейне

👁️ Live-мониторинг - Транзакции в реальном времени, новые блоки

💰 Сбор средств - Ручной и автоматический сбор

⚙️ Конфигурация - Редактирование настроек через веб-интерфейс

📝 Логи - Просмотр логов в реальном времени

🔐 Безопасность - Аутентификация, HTTPS, CORS

REST API:
bash
# Аутентификация
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"ваш_пароль"}'

# Получение статуса
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8080/api/v1/status

# Получение баланса
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8080/api/v1/nodes/LTC/balance/ltc1q...

# WebSocket для реального времени
ws://localhost:8080/api/v1/ws
⚙️ Конфигурация
Шаг 1: Создание файла окружения
bash
# Создайте .env файл в корне проекта
cat > .env << EOL
# Единый API ключ Nownodes для всех монет
NOWNODES_API_KEY=ваш_api_ключ_от_nownodes

# Мастер-адреса для сбора средств
LTC_MASTER_ADDRESS=ltc1qваш_мастер_адрес
DOGE_MASTER_ADDRESS=Dваш_мастер_адрес
BTC_MASTER_ADDRESS=bc1qваш_мастер_адрес

# Настройки веб-панели
NODE_MANAGER_ADMIN_USERNAME=admin
NODE_MANAGER_ADMIN_PASSWORD=ваш_сложный_пароль
NODE_MANAGER_JWT_SECRET=ваш_секретный_ключ

# Дополнительные настройки
LOG_LEVEL=INFO
DB_PATH=node_data.db
EOL
Шаг 2: Создание конфигурационного файла
bash
# Автоматическая генерация шаблона
node-manager init
Или создайте node_config.yaml вручную:

yaml
# node_config.yaml
nownodes:
  api_key: "${NOWNODES_API_KEY}"  # Единый ключ из .env файла
  timeout: 30
  max_retries: 3

coins:
  LTC:
    enabled: true
    blockbook_url: "https://ltcbook.nownodes.io"
    rpc_url: "https://ltc.nownodes.io"
    network: "mainnet"
    master_address: "${LTC_MASTER_ADDRESS}"
    min_collection_amount: 0.001
    collection_fee: 0.0001
    required_confirmations: 3
    
  DOGE:
    enabled: true
    blockbook_url: "https://dogebook.nownodes.io"
    rpc_url: "https://doge.nownodes.io"
    network: "mainnet"
    master_address: "${DOGE_MASTER_ADDRESS}"
    min_collection_amount: 10.0
    collection_fee: 1.0
    required_confirmations: 6

# Веб-панель управления
web_server:
  enabled: true
  host: "0.0.0.0"
  port: 8080
  api_prefix: "/api/v1"
  enable_web_ui: true
  enable_api: true
  allow_cors: true
  session_timeout: 3600
  rate_limit: 100

# Аутентификация
auth:
  enabled: true
  admin_username: "${NODE_MANAGER_ADMIN_USERNAME}"
  admin_password_hash: "${NODE_MANAGER_ADMIN_PASSWORD_HASH}"
  jwt_secret: "${NODE_MANAGER_JWT_SECRET}"
  jwt_algorithm: "HS256"

services:
  monitoring:
    enabled: true
    check_interval: 1800  # 30 минут
    
  collection:
    enabled: true
    auto_start: true
Шаг 3: Запуск системы
bash
# Запуск веб-панели (рекомендуется)
node-manager-web

# Или запуск только бэкенда
python your_bot.py
🏗️ Архитектура
Структура модуля:
text
node_manager/
├── __init__.py              # Основной экспорт
├── node_manager.py          # Главный менеджер
├── node_config.py          # Конфигурация
├── cli.py                  # CLI интерфейс
├── core/                   # Ядро модуля
│   ├── base_node.py       # Базовый класс ноды
│   ├── node_factory.py    # Фабрика создания нод
│   ├── litecoin.py       # Реализация Litecoin
│   ├── dogecoin.py       # Реализация Dogecoin
│   └── bitcoin.py        # Реализация Bitcoin
├── web/                    # Веб-панель
│   ├── server.py         # Веб-сервер и API
│   ├── static/           # Статические файлы
│   └── templates/        # HTML шаблоны
├── api/                   # Клиенты API
│   ├── rpc.py            # RPC клиент
│   ├── blockbook.py      # Blockbook API клиент
│   └── websocket.py      # WebSocket клиент
├── services/              # Сервисы
│   ├── monitor.py        # Мониторинг транзакций
│   ├── collector.py      # Сбор средств
│   └── manager.py        # Основной менеджер
└── utils/                 # Утилиты
    ├── config.py         # Загрузка конфигов
    ├── exceptions.py     # Кастомные исключения
    └── validators.py     # Валидация адресов
Взаимодействие компонентов:
text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Веб-панель    │    │   REST API      │    │   Telegram Bot  │
│   (Браузер)     │◄──►│   (aiohttp)     │◄──►│   (aiogram)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   NodeManager   │    │   NodeConfig    │    │   Мониторинг    │
│                 │◄──►│                 │◄──►│                 │
│  - Управление   │    │  - Конфигурация │    │  - WebSocket    │
│  - Координация  │    │  - Настройки    │    │  - Оповещения   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │
        ▼
┌─────────────────┐    ┌─────────────────┐
│   BaseNode      │    │    Nownodes     │
│                 │◄──►│      API        │
│  - Балансы      │    │                 │
│  - Транзакции   │    └─────────────────┘
│  - Подключение  │
└─────────────────┘
📡 API Reference
NodeManager
Основной класс для управления всеми нодами.

python
from node_manager import NodeManager

# Инициализация
manager = NodeManager(
    config_path="node_config.yaml",  # Путь к конфигурации
    api_key="ваш_ключ"               # API ключ (опционально, если есть в конфиге)
)

# Основные методы
await manager.get_node("LTC")                    # Получить ноду
await manager.start_monitoring("LTC", callback)  # Запустить мониторинг
await manager.monitor_address("LTC", "адрес")   # Добавить адрес в мониторинг
await manager.create_collector("LTC", ...)      # Создать сборщик
await manager.start_auto_collection()           # Запустить автосбор
await manager.stop()                            # Остановить все сервисы
await manager.get_stats()                       # Получить статистику
Веб-API (REST)
Метод	Путь	Описание
POST	/api/v1/auth/login	Аутентификация
GET	/api/v1/status	Статус системы
GET	/api/v1/nodes	Список нод
POST	/api/v1/nodes/{coin}/connect	Подключить ноду
GET	/api/v1/nodes/{coin}/balance/{address}	Баланс адреса
POST	/api/v1/monitoring/start	Запуск мониторинга
GET	/api/v1/ws	WebSocket для real-time
🤖 Примеры
Пример 1: Веб-панель с аутентификацией
python
# run_web.py
import asyncio
from node_manager.web.server import start_web_server

async def main():
    # Запуск веб-панели на порту 8080
    server = await start_web_server(
        config={
            'host': '0.0.0.0',
            'port': 8080,
            'auth_enabled': True,
            'admin_username': 'admin',
            'admin_password': 'secure_password_123'
        }
    )
    
    print(f"Веб-панель запущена: http://0.0.0.0:8080")
    print(f"Логин: admin")
    print(f"Пароль: secure_password_123")
    
    # Бесконечный цикл
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
Пример 2: Интеграция с Telegram ботом
python
# telegram_bot.py
import asyncio
from aiogram import Bot, Dispatcher, types
from node_manager import NodeManager

bot = Bot(token="ВАШ_TELEGRAM_TOKEN")
dp = Dispatcher(bot)
manager = NodeManager()

@dp.message_handler(commands=['status'])
async def cmd_status(message: types.Message):
    stats = await manager.get_stats()
    
    text = "📊 Статус нод:\n\n"
    for coin, info in stats['nodes'].items():
        status = "✅" if info['connected'] else "❌"
        text += f"{status} {coin}: "
        if info['connected']:
            text += f"Блок {info['block_height']}\n"
        else:
            text += f"Ошибка\n"
    
    await message.answer(text)

@dp.message_handler(commands=['balance'])
async def cmd_balance(message: types.Message):
    args = message.get_args().split()
    if len(args) != 2:
        await message.answer("Используйте: /balance LTC ltc1q...")
        return
    
    coin, address = args[0], args[1]
    node = await manager.get_node(coin)
    balance = await node.get_balance(address)
    
    await message.answer(f"Баланс: {balance['total']} {coin}")

async def main():
    # Запуск мониторинга
    await manager.start_monitoring_for_all(
        lambda coin, data: handle_transaction(coin, data)
    )
    
    # Запуск бота
    await dp.start_polling()

async def handle_transaction(coin, data):
    """Отправка уведомлений в Telegram"""
    if data.get('type') == 'transaction':
        tx = data.get('transaction', {})
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"💰 Новая транзакция {coin}:\n"
                 f"TXID: {tx.get('txid')[:20]}...\n"
                 f"Сумма: {tx.get('amount', 0):.8f}"
        )

asyncio.run(main())
Пример 3: Мониторинг через веб-интерфейс
html
<!-- custom_dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Мой Node Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Мониторинг нод</h1>
    
    <div id="nodes"></div>
    <canvas id="blockChart" width="400" height="200"></canvas>
    
    <script>
        let token = localStorage.getItem('token');
        
        async function login() {
            const res = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: 'admin',
                    password: 'ваш_пароль'
                })
            });
            
            const data = await res.json();
            token = data.token;
            localStorage.setItem('token', token);
        }
        
        async function loadNodes() {
            const res = await fetch('/api/v1/nodes', {
                headers: {'Authorization': `Bearer ${token}`}
            });
            
            const nodes = await res.json();
            renderNodes(nodes);
        }
        
        function renderNodes(nodes) {
            const container = document.getElementById('nodes');
            container.innerHTML = nodes.map(node => `
                <div class="node">
                    <h3>${node.coin}</h3>
                    <p>Статус: ${node.connected ? '✅' : '❌'}</p>
                    <p>Блоков: ${node.block_height || 0}</p>
                </div>
            `).join('');
        }
        
        // Обновление каждые 10 секунд
        setInterval(loadNodes, 10000);
        
        // Запуск
        login().then(loadNodes);
    </script>
</body>
</html>
🔧 Развертывание на сервере
Установка на Ubuntu 20.04/22.04:
bash
# 1. Обновление системы
sudo apt update && sudo apt upgrade -y

# 2. Установка Python и pip
sudo apt install python3.9 python3-pip python3-venv -y

# 3. Создание пользователя
sudo adduser node-manager
sudo usermod -aG sudo node-manager
su - node-manager

# 4. Установка Node Manager
git clone https://github.com/glebkoxan36/node-manager.git
cd node-manager
python3 -m venv venv
source venv/bin/activate
pip install -e .

# 5. Настройка конфигурации
node-manager init
nano .env  # Редактируем настройки

# 6. Настройка systemd сервиса
sudo nano /etc/systemd/system/node-manager-web.service
Systemd сервис:
ini
[Unit]
Description=Node Manager Web Server
After=network.target

[Service]
Type=simple
User=node-manager
WorkingDirectory=/home/node-manager/node-manager
Environment="PATH=/home/node-manager/node-manager/venv/bin"
Environment="NODE_MANAGER_ADMIN_PASSWORD=ваш_сложный_пароль"
ExecStart=/home/node-manager/node-manager/venv/bin/node-manager-web \
  --host 0.0.0.0 \
  --port 8080 \
  --username admin
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
Настройка Nginx для HTTPS:
nginx
# /etc/nginx/sites-available/node-manager
server {
    listen 80;
    server_name ваш-домен.ru;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ваш-домен.ru;
    
    ssl_certificate /etc/letsencrypt/live/ваш-домен.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ваш-домен.ru/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
Настройка брандмауэра:
bash
# Открываем порты
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Проверяем
sudo ufw status
📊 Мониторинг и логирование
Просмотр логов:
bash
# Логи systemd сервиса
sudo journalctl -u node-manager-web -f

# Файловые логи
tail -f node_manager.log

# Через веб-панель
http://ваш-сервер:8080/logs
Мониторинг Prometheus:
python
# prometheus_exporter.py
from prometheus_client import start_http_server, Gauge, Counter
import asyncio
from node_manager import NodeManager

NODE_BLOCK_HEIGHT = Gauge('node_block_height', 'Block height', ['coin'])
NODE_CONNECTIONS = Gauge('node_connections', 'Connections status', ['coin'])

async def export_metrics():
    manager = NodeManager()
    start_http_server(9090)
    
    while True:
        stats = await manager.get_stats()
        
        for coin, info in stats['nodes'].items():
            NODE_CONNECTIONS.labels(coin=coin).set(1 if info['connected'] else 0)
            if info.get('block_height'):
                NODE_BLOCK_HEIGHT.labels(coin=coin).set(info['block_height'])
        
        await asyncio.sleep(30)

asyncio.run(export_metrics())
Графики в Grafana:
Добавьте Prometheus как источник данных

Импортируйте дашборд с графиками:

Высота блоков по монетам

Статус подключения

Количество транзакций

Использование памяти и CPU

🔐 Безопасность
Рекомендации по безопасности:
Всегда используйте HTTPS в продакшене

Измените пароль по умолчанию сразу после установки

Используйте сложные пароли (12+ символов, буквы, цифры, спецсимволы)

Ограничьте доступ по IP в настройках брандмауэра

Регулярно обновляйте систему и зависимости

Не храните приватные ключи в конфигурационных файлах

Используйте отдельного пользователя для запуска сервиса

Настройте автоматическое резервное копирование конфигурации

Переменные окружения для безопасности:
bash
# .env.production
NOWNODES_API_KEY=your_production_key_here
NODE_MANAGER_ADMIN_PASSWORD=$(openssl rand -base64 32)
NODE_MANAGER_JWT_SECRET=$(openssl rand -base64 64)
LTC_MASTER_ADDRESS=ltc1qproduction_address
🛠️ Отладка и устранение неисправностей
Проверка подключения:
bash
# Тестирование всех нод
node-manager test

# Тестирование конкретной ноды
node-manager test --coin LTC

# Проверка статуса
node-manager status
Логирование:
python
import logging

# Включение подробного логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
Частые проблемы и решения:
"API key not found" - Проверьте .env файл и переменные окружения

"Connection timeout" - Проверьте сетевые настройки и доступность Nownodes

"Invalid address" - Проверьте формат крипто-адреса

"Web server not starting" - Проверьте, не занят ли порт 8080

"Authentication failed" - Проверьте логин/пароль в .env файле

🤝 Вклад в проект
Установка для разработки:
bash
git clone https://github.com/glebkoxan36/node-manager.git
cd node-manager
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
Запуск тестов:
bash
pytest tests/ -v
pytest tests/ --cov=node_manager --cov-report=html
tox
Стиль кода:
bash
black node_manager/
flake8 node_manager/
mypy node_manager/
isort node_manager/
