Node Manager - Универсальный менеджер криптовалютных нод

🌟 Особенности

🚀 Быстрый старт

📦 Установка

⚙️ Конфигурация

🏗️ Архитектура

💡 Использование

🤖 Примеры

🔧 API Reference

➕ Добавление монет

📊 Мониторинг

🛠️ Отладка

📈 Производительность

🤝 Вклад в проект

📄 Лицензия

🌟 Особенности
✅ Полная поддержка Nownodes
Единый API ключ для всех монет

Автоматическое подключение к Blockbook и RPC API

WebSocket для реального мониторинга

✅ Мульти-монетная поддержка
Litecoin (LTC) - полная поддержка

Dogecoin (DOGE) - полная поддержка

Bitcoin (BTC) - полная поддержка

Легко добавить любую другую монету

✅ Автоматизация
Автоматический мониторинг транзакций

Автоматический сбор средств на мастер-адрес

Периодическая проверка балансов

Отписка от адресов после сбора

✅ Безопасность
Централизованное управление ключами

Валидация всех адресов

Безопасное хранение конфигурации

Поддержка переменных окружения

✅ Простота использования
Установка одной командой

Конфигурация через YAML/JSON

Готовые примеры ботов

Подробная документация

🚀 Быстрый старт
Установка за 30 секунд:
bash
# Установите модуль
pip install git+https://github.com/yourusername/node-manager.git

# Создайте конфигурацию
python -c "from node_manager.nodeconfig import NodeConfig; NodeConfig.generate_config_template()"

# Отредактируйте файл .env и node_config.yaml
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
📦 Установка
Способ 1: Из GitHub (рекомендуется)
bash
# Последняя версия из main ветки
pip install git+https://github.com/yourusername/node-manager.git

# Конкретная версия
pip install git+https://github.com/yourusername/node-manager.git@v2.0.0

# Конкретная ветка
pip install git+https://github.com/yourusername/node-manager.git@develop
Способ 2: Локальная установка
bash
# Клонирование репозитория
git clone https://github.com/yourusername/node-manager.git
cd node-manager

# Установка в режиме разработки
pip install -e .

# Или установка как пакет
python setup.py install
Способ 3: Из PyPI (после публикации)
bash
pip install node-manager
Зависимости
Модуль автоматически установит:

aiohttp>=3.8.0 - Асинхронные HTTP запросы

websockets>=11.0.0 - WebSocket клиент

PyYAML>=6.0 - Работа с YAML конфигурацией

python-dotenv>=1.0.0 - Переменные окружения

bip-utils>=2.7.0 - Валидация адресов

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

# Дополнительные настройки
LOG_LEVEL=INFO
DB_PATH=node_data.db
EOL
Шаг 2: Создание конфигурационного файла
python
# Автоматическая генерация шаблона
python -c "from node_manager.nodeconfig import NodeConfig; NodeConfig.generate_config_template('node_config.yaml')"
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

services:
  monitoring:
    enabled: true
    check_interval: 1800  # 30 минут
    
  collection:
    enabled: true
    auto_start: true
Шаг 3: Управление конфигурацией
python
from node_manager.nodeconfig import NodeConfig

# Обновление API ключа для всех монет
NodeConfig.update_api_key("новый_ключ")

# Включение/выключение монет
NodeConfig.enable_coin("BTC", True)  # Включить Bitcoin

# Установка мастер-адреса
NodeConfig.set_master_address("LTC", "ltc1qновый_адрес")

# Изменение параметров сбора
NodeConfig.set_collection_params(
    coin_type="LTC",
    min_amount=0.002,     # Новый минимум
    fee=0.0002,           # Новая комиссия
    confirmations=6       # Требуемые подтверждения
)

# Получение текущей конфигурации
config = NodeConfig.load_config()
print(f"Включенные монеты: {NodeConfig.get_enabled_coins(config)}")
🏗️ Архитектура
Структура модуля:
text
node_manager/
├── __init__.py              # Основной экспорт
├── nodeconfig.py           # Центральная конфигурация
├── core/                   # Ядро модуля
│   ├── base_node.py       # Базовый класс ноды
│   ├── node_factory.py    # Фабрика создания нод
│   ├── litecoin.py       # Реализация Litecoin
│   ├── dogecoin.py       # Реализация Dogecoin
│   └── bitcoin.py        # Реализация Bitcoin
├── api/                    # Клиенты API
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
│     Ваш бот     │    │   NodeManager   │    │   NodeConfig    │
│                 │◄──►│                 │◄──►│                 │
│  - Команды      │    │  - Управление   │    │  - Конфигурация │
│  - Пользователи │    │  - Координация  │    │  - Настройки    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   BaseNode      │    │   Мониторинг    │    │    Сборщик      │
│                 │◄──►│                 │◄──►│                 │
│  - Балансы      │    │  - WebSocket    │    │  - UTXO сбор    │
│  - Транзакции   │    │  - Оповещения   │    │  - Подпись      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │
        ▼
┌─────────────────┐    ┌─────────────────┐
│    Nownodes     │    │   Blockbook     │
│      RPC        │    │      API        │
└─────────────────┘    └─────────────────┘
💡 Использование
Базовые операции:
python
import asyncio
from node_manager import NodeManager

async def basic_operations():
    # Инициализация менеджера
    manager = NodeManager(config_path="node_config.yaml")
    
    # 1. Получение ноды
    ltc_node = await manager.get_node("LTC")
    
    # 2. Проверка баланса
    balance = await ltc_node.get_balance("ltc1q...")
    print(f"Баланс: {balance['total']} LTC")
    
    # 3. Получение информации об адресе
    info = await ltc_node.get_address_info("ltc1q...")
    print(f"Транзакций: {info['transaction_count']}")
    
    # 4. Получение UTXO
    utxos = await ltc_node.get_address_utxos("ltc1q...")
    print(f"Найдено UTXO: {len(utxos)}")
    
    # 5. Валидация адреса
    validation = await ltc_node.validate_address("ltc1q...")
    print(f"Адрес валиден: {validation['is_valid']}")
    
    # 6. Получение информации о блокчейне
    blockchain = await ltc_node.get_blockchain_info()
    print(f"Высота блока: {blockchain['blocks']}")

asyncio.run(basic_operations())
Транзакции:
python
async def transaction_operations():
    manager = NodeManager()
    node = await manager.get_node("LTC")
    
    # 1. Получение информации о транзакции
    tx_info = await node.get_transaction("txid_пример")
    print(f"Транзакция: {tx_info['amount']} LTC")
    
    # 2. Создание сырой транзакции
    inputs = [
        {
            "txid": "предыдущий_txid",
            "vout": 0,
            "address": "исходный_адрес"
        }
    ]
    
    outputs = {
        "ltc1qполучатель": 0.001  # 0.001 LTC
    }
    
    raw_tx = await node.create_raw_transaction(inputs, outputs)
    print(f"Создана сырая транзакция: {raw_tx[:50]}...")
    
    # 3. Подписание транзакции
    private_keys = ["ваш_приватный_ключ"]
    signed_tx = await node.sign_raw_transaction(raw_tx, private_keys)
    
    if signed_tx['complete']:
        # 4. Отправка транзакции
        txid = await node.send_transaction(signed_tx['hex'])
        print(f"Транзакция отправлена: {txid}")
🤖 Примеры
Пример 1: Простой мониторинг адресов
python
"""
simple_monitor.py - Простой мониторинг адресов Litecoin
"""

import asyncio
import logging
from node_manager import NodeManager

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_transaction(coin, data):
    """Обработчик новых транзакций"""
    address = data.get('address')
    tx = data.get('transaction', {})
    
    if address and tx:
        logger.info(f"💰 Новая транзакция для {coin}:{address}")
        logger.info(f"   TXID: {tx.get('txid')}")
        logger.info(f"   Сумма: {tx.get('amount', 0)}")
        logger.info(f"   Подтверждения: {tx.get('confirmations', 0)}")

async def main():
    """Основная функция"""
    logger.info("🚀 Запуск мониторинга...")
    
    # Инициализация менеджера
    manager = NodeManager()
    
    try:
        # Получение ноды Litecoin
        ltc_node = await manager.get_node("LTC")
        logger.info(f"✅ Подключено к {ltc_node.coin_name}")
        
        # Запуск мониторинга с обработчиком
        await manager.start_monitoring("LTC", handle_transaction)
        
        # Добавление адресов для мониторинга
        addresses = [
            "ltc1q489hgnahvr9zspytmsu6vew8nc4j6c3aqkdvxg",
            "ltc1qexample1addressfortesting",
            "ltc1qexample2addressfortesting"
        ]
        
        for address in addresses:
            # Валидация адреса перед добавлением
            validation = await ltc_node.validate_address(address)
            if validation['is_valid']:
                await manager.monitor_address("LTC", address)
                logger.info(f"👁️  Мониторим адрес: {address}")
            else:
                logger.warning(f"⚠️  Невалидный адрес: {address}")
        
        logger.info("📡 Мониторинг запущен. Нажмите Ctrl+C для остановки.")
        
        # Бесконечный цикл
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Остановка по команде пользователя")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
    finally:
        # Корректное завершение
        await manager.stop()

if __name__ == "__main__":
    asyncio.run(main())
Пример 2: Автоматический сборщик средств
python
"""
auto_collector.py - Автоматический сбор средств с адресов
"""

import asyncio
import logging
from datetime import datetime
from node_manager import NodeManager
from node_manager.nodeconfig import NodeConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoCollector:
    def __init__(self):
        self.manager = None
        self.collectors = {}
        self.addresses_db = {}
        
    async def start(self):
        """Запуск сборщика"""
        logger.info("🚀 Запуск автоматического сборщика...")
        
        # Загрузка конфигурации
        config = NodeConfig.load_config()
        enabled_coins = NodeConfig.get_enabled_coins(config)
        
        # Инициализация менеджера
        self.manager = NodeManager(config=config)
        
        # Инициализация сборщиков для каждой монеты
        for coin in enabled_coins:
            coin_config = NodeConfig.get_coin_config(coin, config)
            collector = await self.manager.create_collector(
                coin,
                master_address=coin_config.get('master_address'),
                fee=coin_config.get('collection_fee', 0.0001)
            )
            self.collectors[coin] = collector
        
        # Загрузка адресов (в реальном боте - из базы данных)
        await self.load_addresses()
        
        # Запуск периодического сбора
        asyncio.create_task(self.collection_worker())
        
        # Запуск мониторинга транзакций
        await self.manager.start_monitoring_for_all(self.handle_transaction)
        
        logger.info("✅ Сборщик запущен")
        
        # Основной цикл
        while True:
            await asyncio.sleep(1)
    
    async def load_addresses(self):
        """Загрузка адресов для мониторинга"""
        # Пример адресов (в реальном боте загружайте из БД)
        self.addresses_db = {
            "ltc1qaddress1": {
                "coin": "LTC",
                "private_key": "ваш_приватный_ключ_1",  # Безопасное хранение!
                "added": datetime.now(),
                "collected": False
            },
            "ltc1qaddress2": {
                "coin": "LTC",
                "private_key": "ваш_приватный_ключ_2",
                "added": datetime.now(),
                "collected": False
            }
        }
        
        # Добавление адресов в мониторинг
        for address, data in self.addresses_db.items():
            if not data['collected']:
                await self.manager.monitor_address(data['coin'], address)
                logger.info(f"👁️  Добавлен в мониторинг: {address}")
    
    async def collection_worker(self):
        """Фоновый воркер для сбора"""
        check_interval = 1800  # 30 минут
        
        while True:
            try:
                logger.info("🔄 Проверка адресов для сбора...")
                
                for address, data in self.addresses_db.items():
                    if not data['collected']:
                        coin = data['coin']
                        
                        # Проверяем возможность сбора
                        collector = self.collectors[coin]
                        estimation = await collector.estimate_collection(address)
                        
                        if estimation.get('can_collect'):
                            logger.info(f"💰 Адрес готов к сбору: {address}")
                            
                            # Собираем средства
                            result = await collector.collect_from_address(
                                address, 
                                data['private_key']
                            )
                            
                            if result and result.get('success'):
                                logger.info(f"✅ Средства собраны: {result.get('amount')} {coin}")
                                data['collected'] = True
                                data['collected_at'] = datetime.now()
                                data['txid'] = result.get('txid')
                                
                                # Отписываемся от адреса
                                await self.manager.unmonitor_address(coin, address)
                            
                            # Пауза между сборами
                            await asyncio.sleep(10)
                
                logger.info(f"⏱️  Следующая проверка через {check_interval/60} минут")
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"❌ Ошибка в collection_worker: {e}")
                await asyncio.sleep(60)
    
    async def handle_transaction(self, coin, data):
        """Обработчик транзакций"""
        address = data.get('address')
        transaction = data.get('transaction', {})
        
        if address and transaction:
            confirmations = transaction.get('confirmations', 0)
            
            # Если транзакция подтверждена, проверяем возможность сбора
            if confirmations >= 3:
                logger.info(f"✅ Подтвержденная транзакция для {address}")
                
                # Немедленно проверяем возможность сбора
                if address in self.addresses_db and not self.addresses_db[address]['collected']:
                    collector = self.collectors[coin]
                    estimation = await collector.estimate_collection(address)
                    
                    if estimation.get('can_collect'):
                        await collector.collect_from_address(
                            address, 
                            self.addresses_db[address]['private_key']
                        )
    
    async def stop(self):
        """Остановка сборщика"""
        if self.manager:
            await self.manager.stop()
        logger.info("🛑 Сборщик остановлен")

async def main():
    collector = AutoCollector()
    
    try:
        await collector.start()
    except KeyboardInterrupt:
        logger.info("🛑 Остановка по команде пользователя")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        await collector.stop()

if __name__ == "__main__":
    asyncio.run(main())
Пример 3: Мульти-монетный бот с Telegram интерфейсом
python
"""
telegram_bot.py - Бот с Telegram интерфейсом для управления нодами
"""

import asyncio
import logging
from typing import Dict, Any
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from node_manager import NodeManager
from node_manager.nodeconfig import NodeConfig

# Настройки
API_TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"
ADMIN_IDS = [123456789]  # ID администраторов

# Инициализация
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Node Manager
node_manager = None

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """Команда /start"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Доступ запрещен")
        return
    
    await message.answer(
        "🤖 Node Manager Bot\n\n"
        "Доступные команды:\n"
        "/status - Статус нод\n"
        "/balance <адрес> - Баланс адреса\n"
        "/monitor <монета> <адрес> - Мониторинг адреса\n"
        "/collect <адрес> - Собрать средства\n"
        "/stats - Статистика\n"
        "/coins - Список монет\n"
        "/stop - Остановить мониторинг"
    )

@dp.message_handler(commands=['status'])
async def cmd_status(message: types.Message):
    """Статус нод"""
    if not node_manager:
        await message.answer("❌ Node Manager не инициализирован")
        return
    
    try:
        status_text = "📊 Статус нод:\n\n"
        
        # Получаем конфигурацию
        config = NodeConfig.load_config()
        enabled_coins = NodeConfig.get_enabled_coins(config)
        
        for coin in enabled_coins:
            try:
                node = await node_manager.get_node(coin)
                info = await node.get_blockchain_info()
                
                if 'error' not in info:
                    status_text += f"✅ {coin}:\n"
                    status_text += f"   Блоков: {info.get('blocks', 0)}\n"
                    status_text += f"   Сеть: {info.get('chain', 'unknown')}\n"
                else:
                    status_text += f"❌ {coin}: Ошибка подключения\n"
                    
            except Exception as e:
                status_text += f"❌ {coin}: {str(e)[:50]}\n"
        
        await message.answer(status_text)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message_handler(commands=['balance'])
async def cmd_balance(message: types.Message):
    """Проверка баланса адреса"""
    args = message.get_args().split()
    if len(args) < 2:
        await message.answer("❌ Используйте: /balance <монета> <адрес>")
        return
    
    coin, address = args[0].upper(), args[1]
    
    try:
        node = await node_manager.get_node(coin)
        balance = await node.get_balance(address)
        
        if 'error' in balance:
            await message.answer(f"❌ Ошибка: {balance['error']}")
        else:
            response = (
                f"💰 Баланс {coin}:\n"
                f"Адрес: {address}\n"
                f"Подтверждено: {balance.get('confirmed', 0):.8f}\n"
                f"Неподтверждено: {balance.get('unconfirmed', 0):.8f}\n"
                f"Всего: {balance.get('total', 0):.8f}"
            )
            await message.answer(response)
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message_handler(commands=['monitor'])
async def cmd_monitor(message: types.Message):
    """Добавление адреса в мониторинг"""
    args = message.get_args().split()
    if len(args) < 2:
        await message.answer("❌ Используйте: /monitor <монета> <адрес>")
        return
    
    coin, address = args[0].upper(), args[1]
    
    try:
        node = await node_manager.get_node(coin)
        validation = await node.validate_address(address)
        
        if not validation['is_valid']:
            await message.answer(f"❌ Невалидный адрес {coin}")
            return
        
        await node_manager.monitor_address(coin, address)
        await message.answer(f"✅ Адрес добавлен в мониторинг: {coin}:{address}")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message_handler(commands=['stats'])
async def cmd_stats(message: types.Message):
    """Статистика"""
    try:
        stats = await node_manager.get_stats()
        
        response = "📈 Статистика:\n\n"
        response += f"Нод подключено: {stats.get('nodes_connected', 0)}\n"
        response += f"Мониторов активно: {stats.get('monitors_running', 0)}\n"
        response += f"Адресов в мониторинге: {stats.get('addresses_monitored', 0)}\n"
        response += f"Сборов выполнено: {stats.get('collections_completed', 0)}\n"
        
        await message.answer(response)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message_handler(commands=['coins'])
async def cmd_coins(message: types.Message):
    """Список поддерживаемых монет"""
    config = NodeConfig.load_config()
    enabled_coins = NodeConfig.get_enabled_coins(config)
    
    response = "🪙 Поддерживаемые монеты:\n\n"
    for coin in enabled_coins:
        coin_config = NodeConfig.get_coin_config(coin, config)
        response += f"• {coin} ({coin_config.get('coin_name')})\n"
        response += f"  Сеть: {coin_config.get('network')}\n"
        response += f"  Мастер: {coin_config.get('master_address', 'не установлен')[:20]}...\n"
    
    await message.answer(response)

async def on_startup(dp):
    """Запуск при старте бота"""
    global node_manager
    
    logging.info("🚀 Запуск Node Manager Bot...")
    
    # Инициализация Node Manager
    node_manager = NodeManager()
    
    # Запуск мониторинга
    await node_manager.start_monitoring_for_all(
        lambda coin, data: handle_node_event(coin, data)
    )
    
    logging.info("✅ Node Manager Bot запущен")

async def on_shutdown(dp):
    """Остановка при выключении"""
    global node_manager
    
    logging.info("🛑 Остановка Node Manager Bot...")
    
    if node_manager:
        await node_manager.stop()
    
    logging.info("✅ Node Manager Bot остановлен")

async def handle_node_event(coin: str, data: Dict[str, Any]):
    """Обработка событий от нод"""
    event_type = data.get('type')
    
    if event_type == 'transaction':
        address = data.get('address')
        tx = data.get('transaction', {})
        
        # Отправляем уведомление администраторам
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"💰 Новая транзакция {coin}:\n"
                    f"Адрес: {address}\n"
                    f"TXID: {tx.get('txid')}\n"
                    f"Сумма: {tx.get('amount', 0):.8f}"
                )
            except Exception as e:
                logging.error(f"Ошибка отправки уведомления: {e}")

async def main():
    """Основная функция"""
    # Запуск бота
    await dp.start_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Запуск с обработчиками событий
    from aiogram import executor
    executor.start_polling(
        dp, 
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )
🔧 API Reference
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
BaseNode
Базовый класс для всех криптовалютных нод.

python
# Получение ноды через менеджер
node = await manager.get_node("LTC")

# Основные методы
await node.connect()                          # Подключиться к ноде
await node.disconnect()                       # Отключиться
await node.get_balance("адрес")              # Получить баланс
await node.get_address_info("адрес")         # Информация об адресе
await node.get_transaction("txid")           # Информация о транзакции
await node.get_address_utxos("адрес")        # Получить UTXO
await node.send_transaction("сырая_транзакция")  # Отправить транзакцию
await node.validate_address("адрес")         # Валидация адреса
await node.get_blockchain_info()             # Информация о блокчейне
await node.estimate_fee(blocks=3)            # Оценить комиссию
await node.create_raw_transaction(inputs, outputs)  # Создать транзакцию
await node.sign_raw_transaction(raw_tx, private_keys)  # Подписать транзакцию
await node.get_transaction_history("адрес", limit=10)  # История транзакций
await node.batch_get_balances(["адрес1", "адрес2"])  # Пакетный запрос балансов
TransactionMonitor
Сервис мониторинга транзакций через WebSocket.

python
from node_manager.services.monitor import TransactionMonitor

monitor = TransactionMonitor(
    node=node,                               # Экземпляр ноды
    on_transaction=callback_function,        # Функция обратного вызова
    config=monitor_config                    # Конфигурация мониторинга
)

await monitor.start()                        # Запустить мониторинг
await monitor.subscribe_address("адрес")    # Подписаться на адрес
await monitor.unsubscribe_address("адрес")  # Отписаться от адреса
await monitor.stop()                         # Остановить мониторинг
is_running = monitor.is_running()            # Проверить статус
addresses = monitor.get_subscribed_addresses()  # Получить список адресов
FundsCollector
Сервис для сбора средств на мастер-адрес.

python
from node_manager.services.collector import FundsCollector

collector = FundsCollector(
    node=node,                               # Экземпляр ноды
    master_address="мастер_адрес",          # Адрес для сбора
    fee=0.0001                               # Комиссия сбора
)

# Сбор с одного адреса
result = await collector.collect_from_address(
    address="исходный_адрес",
    private_key="приватный_ключ"            # Опционально
)

# Пакетный сбор
results = await collector.collect_multiple(
    addresses=["адрес1", "адрес2"],
    private_keys={"адрес1": "ключ1"}        # Словарь ключей
)

# Оценка сбора
estimation = await collector.estimate_collection("адрес")

# Настройки
collector.set_fee(0.0002)                   # Установить комиссию
collector.set_min_amount(0.002)             # Установить минимальную сумму
NodeConfig
Центральный класс для управления конфигурацией.

python
from node_manager.nodeconfig import NodeConfig

# Загрузка конфигурации
config = NodeConfig.load_config("node_config.yaml")

# Управление
NodeConfig.update_api_key("новый_ключ")                     # Обновить API ключ
NodeConfig.enable_coin("BTC", True)                        # Включить монету
NodeConfig.set_master_address("LTC", "новый_адрес")        # Установить мастер-адрес
NodeConfig.set_collection_params("LTC", min_amount=0.002)  # Параметры сбора

# Получение информации
enabled_coins = NodeConfig.get_enabled_coins()             # Включенные монеты
ltc_config = NodeConfig.get_coin_config("LTC")             # Конфигурация монеты
NodeConfig.generate_config_template()                       # Генерация шаблона
➕ Добавление монет
Шаг 1: Создание класса монеты
python
# node_manager/core/ethereum.py
"""
Реализация ноды Ethereum
"""

import logging
from typing import Dict, List, Any, Union
from decimal import Decimal
from .base_node import BaseNode

logger = logging.getLogger(__name__)

class EthereumNode(BaseNode):
    """Нода Ethereum"""
    
    def __init__(self, **kwargs):
        # Установка специфичных параметров
        kwargs.setdefault('coin_type', 'ETH')
        kwargs.setdefault('coin_name', 'Ethereum')
        kwargs.setdefault('decimals', 18)  # Ethereum использует 18 знаков
        
        # URL для Ethereum (если поддерживается Nownodes)
        if not kwargs.get('blockbook_url'):
            kwargs['blockbook_url'] = 'https://ethbook.nownodes.io'
        if not kwargs.get('rpc_url'):
            kwargs['rpc_url'] = 'https://eth.nownodes.io'
        
        super().__init__(**kwargs)
    
    async def connect(self) -> bool:
        """Подключение к Ethereum ноде"""
        try:
            # Ethereum использует JSON-RPC API
            # Проверяем подключение через web3_clientVersion
            if self.rpc_client:
                result = await self.rpc_client.call("web3_clientVersion", [])
                if 'error' not in result:
                    self._connected = True
                    logger.info(f"Connected to Ethereum node")
                    return True
            
            self._connected = True
            logger.info(f"Connected to Ethereum node")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Ethereum: {e}")
            self._connected = False
            return False
    
    async def get_balance(self, address: str) -> Dict[str, Any]:
        """Получить баланс адреса в ETH"""
        try:
            if not self.rpc_client:
                return {'error': 'RPC client not available'}
            
            # Ethereum использует eth_getBalance
            result = await self.rpc_client.call("eth_getBalance", [address, "latest"])
            
            if 'error' in result:
                return result
            
            # Конвертируем из wei в ETH
            balance_wei = int(result.get('result', '0x0'), 16)
            balance_eth = balance_wei / (10 ** self.decimals)
            
            return {
                'address': address,
                'balance': balance_eth,
                'in_wei': balance_wei,
                'coin': 'ETH'
            }
            
        except Exception as e:
            logger.error(f"Error getting ETH balance: {e}")
            return {'error': str(e)}
    
    # Реализация остальных методов...
    # get_transaction, send_transaction и т.д.

    async def send_transaction(self, raw_tx_hex: str) -> str:
        """Отправить транзакцию Ethereum"""
        try:
            if not self.rpc_client:
                raise Exception("RPC client not available")
            
            # Ethereum использует eth_sendRawTransaction
            result = await self.rpc_client.call("eth_sendRawTransaction", [raw_tx_hex])
            
            if 'error' in result:
                raise Exception(f"RPC error: {result['error']}")
            
            tx_hash = result.get('result')
            logger.info(f"ETH transaction sent: {tx_hash}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"Error sending ETH transaction: {e}")
            raise

    async def estimate_fee(self, blocks: int = 3) -> Dict[str, Any]:
        """Оценить комиссию Gas для Ethereum"""
        try:
            if not self.rpc_client:
                return {'error': 'RPC client not available'}
            
            # Получаем текущий base fee и priority fee
            fee_history = await self.rpc_client.call("eth_feeHistory", [blocks, "latest", [25, 50, 75]])
            
            if 'error' in fee_history:
                # Возвращаем значения по умолчанию
                return {
                    'base_fee': 30,  # Gwei
                    'max_priority_fee': 2,  # Gwei
                    'max_fee': 32,  # Gwei
                    'gas_limit': 21000,
                    'coin': 'ETH'
                }
            
            # Парсим результат
            # ... логика обработки feeHistory ...
            
            return {
                'base_fee': 30,
                'max_priority_fee': 2,
                'max_fee': 32,
                'gas_limit': 21000,
                'coin': 'ETH'
            }
            
        except Exception as e:
            logger.error(f"Error estimating ETH fee: {e}")
            return {'error': str(e)}
Шаг 2: Регистрация монеты в фабрике
python
# В node_manager/core/node_factory.py добавить:

from .ethereum import EthereumNode

class NodeFactory:
    _node_classes = {
        'LTC': LitecoinNode,
        'DOGE': DogecoinNode,
        'BTC': BitcoinNode,
        'ETH': EthereumNode,  # Добавлено
    }
    
    _default_configs = {
        # ... существующие конфиги ...
        'ETH': {
            'blockbook_url': 'https://ethbook.nownodes.io',
            'rpc_url': 'https://eth.nownodes.io',
            'network': 'mainnet',
            'decimals': 18,
            'coin_symbol': 'ETH',
            'coin_name': 'Ethereum',
            'min_collection_amount': 0.01,
            'collection_fee': 0.001,
            'required_confirmations': 12
        }
    }
Шаг 3: Добавление в конфигурацию
yaml
# В node_config.yaml добавить:
coins:
  ETH:
    enabled: true
    blockbook_url: "https://ethbook.nownodes.io"
    rpc_url: "https://eth.nownodes.io"
    network: "mainnet"
    decimals: 18
    coin_symbol: "ETH"
    coin_name: "Ethereum"
    master_address: "0xваш_мастер_адрес"
    min_collection_amount: 0.01
    collection_fee: 0.001
    required_confirmations: 12
Шаг 4: Использование новой монеты
python
# Теперь можно использовать Ethereum
from node_manager import NodeManager

async def use_ethereum():
    manager = NodeManager()
    eth_node = await manager.get_node("ETH")
    
    balance = await eth_node.get_balance("0xадрес")
    print(f"Баланс ETH: {balance['balance']}")
📊 Мониторинг
Встроенный мониторинг:
python
from node_manager import NodeManager

async def monitoring_example():
    manager = NodeManager()
    
    # Запуск мониторинга с кастомным обработчиком
    async def handle_event(coin, data):
        event_type = data.get('type')
        
        if event_type == 'transaction':
            print(f"Новая транзакция {coin}: {data['transaction']['txid']}")
        elif event_type == 'block':
            print(f"Новый блок {coin}: #{data['block']['height']}")
    
    await manager.start_monitoring_for_all(handle_event)
    
    # Добавление адресов для мониторинга
    await manager.monitor_address("LTC", "ltc1q...")
    await manager.monitor_address("DOGE", "D...")
    
    # Получение статистики мониторинга
    stats = await manager.get_monitoring_stats()
    print(f"Адресов в мониторинге: {stats['addresses_monitored']}")
Внешний мониторинг (Prometheus/Grafana):
python
# Пример экспорта метрик в Prometheus
from prometheus_client import start_http_server, Gauge, Counter
import asyncio
from node_manager import NodeManager

# Метрики Prometheus
NODE_BLOCK_HEIGHT = Gauge('node_block_height', 'Block height by coin', ['coin'])
NODE_CONNECTIONS = Gauge('node_connections', 'Node connections status', ['coin'])
TRANSACTIONS_PROCESSED = Counter('transactions_processed', 'Transactions processed', ['coin'])

async def export_metrics():
    """Экспорт метрик для мониторинга"""
    manager = NodeManager()
    
    # Запускаем HTTP сервер для Prometheus
    start_http_server(8000)
    
    while True:
        try:
            # Получаем информацию о каждой ноде
            config = manager.config
            for coin in config.get('coins', {}).keys():
                try:
                    node = await manager.get_node(coin)
                    info = await node.get_blockchain_info()
                    
                    if 'error' not in info:
                        # Экспортируем метрики
                        NODE_BLOCK_HEIGHT.labels(coin=coin).set(info.get('blocks', 0))
                        NODE_CONNECTIONS.labels(coin=coin).set(1)
                    else:
                        NODE_CONNECTIONS.labels(coin=coin).set(0)
                        
                except Exception as e:
                    NODE_CONNECTIONS.labels(coin=coin).set(0)
            
            # Ждем 30 секунд
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"Ошибка экспорта метрик: {e}")
            await asyncio.sleep(60)

# Запуск экспорта метрик
asyncio.run(export_metrics())
Графический дашборд:
html
<!-- Пример простого дашборда -->
<!DOCTYPE html>
<html>
<head>
    <title>Node Manager Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Node Manager Dashboard</h1>
    
    <div class="stats">
        <div class="stat">
            <h3>Block Height</h3>
            <canvas id="blockChart"></canvas>
        </div>
        
        <div class="stat">
            <h3>Addresses Monitored</h3>
            <canvas id="addressChart"></canvas>
        </div>
        
        <div class="stat">
            <h3>Collections</h3>
            <canvas id="collectionChart"></canvas>
        </div>
    </div>
    
    <script>
        // Запрос данных с API
        async function fetchStats() {
            const response = await fetch('/api/stats');
            return await response.json();
        }
        
        // Обновление графиков
        async function updateCharts() {
            const stats = await fetchStats();
            
            // Обновляем блоки
            updateBlockChart(stats.block_heights);
            // Обновляем адреса
            updateAddressChart(stats.addresses);
            // Обновляем сборы
            updateCollectionChart(stats.collections);
        }
        
        // Обновление каждые 30 секунд
        setInterval(updateCharts, 30000);
        updateCharts(); // Первоначальная загрузка
    </script>
</body>
</html>
🛠️ Отладка
Включение подробного логирования:
python
import logging

# Настройка подробного логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# Или через конфигурацию
import yaml
config = {
    'services': {
        'logging': {
            'level': 'DEBUG',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': 'node_debug.log'
        }
    }
}

with open('node_config_debug.yaml', 'w') as f:
    yaml.dump(config, f)
Тестирование подключения:
python
# test_connection.py
import asyncio
import logging
from node_manager import NodeManager

logging.basicConfig(level=logging.DEBUG)

async def test_connections():
    """Тестирование подключения ко всем нодам"""
    manager = NodeManager()
    
    print("🔍 Тестирование подключений...")
    
    # Тестируем каждую монету
    coins_to_test = ["LTC", "DOGE", "BTC"]
    
    for coin in coins_to_test:
        try:
            print(f"\n📡 Тестируем {coin}...")
            
            # Получаем ноду
            node = await manager.get_node(coin)
            
            # Тест 1: Подключение
            print(f"   Подключение... ", end="")
            connected = await node.connect()
            print("✅" if connected else "❌")
            
            if connected:
                # Тест 2: Блокчейн информация
                print(f"   Информация о блокчейне... ", end="")
                info = await node.get_blockchain_info()
                if 'error' not in info:
                    print(f"✅ (Блок: {info.get('blocks', 0)})")
                else:
                    print(f"❌ ({info.get('error', 'Unknown error')})")
                
                # Тест 3: Оценка комиссии
                print(f"   Оценка комиссии... ", end="")
                fee = await node.estimate_fee()
                if 'error' not in fee:
                    print(f"✅ ({fee.get('fee_per_kb')} за KB)")
                else:
                    print(f"❌")
                
                # Тест 4: Валидация тестового адреса
                test_address = {
                    "LTC": "ltc1q489hgnahvr9zspytmsu6vew8nc4j6c3aqkdvxg",
                    "DOGE": "D7i9UYtC6r5jz4g3h2f1d0s9a8w7q6e5r4t3y2u1i",
                    "BTC": "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"
                }.get(coin, "")
                
                if test_address:
                    print(f"   Валидация адреса... ", end="")
                    validation = await node.validate_address(test_address)
                    print("✅" if validation.get('is_valid') else "❌")
            
            # Отключаемся
            await node.disconnect()
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании {coin}: {e}")
    
    print("\n🎯 Тестирование завершено")

asyncio.run(test_connections())
Мониторинг производительности:
python
# performance_monitor.py
import asyncio
import time
import statistics
from node_manager import NodeManager

class PerformanceMonitor:
    def __init__(self):
        self.latencies = {}
        self.manager = NodeManager()
    
    async def measure_method(self, coin, method_name, *args):
        """Измерение времени выполнения метода"""
        try:
            node = await self.manager.get_node(coin)
            method = getattr(node, method_name)
            
            start_time = time.time()
            result = await method(*args)
            elapsed = time.time() - start_time
            
            # Сохраняем результат
            key = f"{coin}.{method_name}"
            if key not in self.latencies:
                self.latencies[key] = []
            
            self.latencies[key].append(elapsed)
            
            return {
                'success': 'error' not in result,
                'time': elapsed,
                'result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'time': 0
            }
    
    async def run_performance_test(self, iterations=10):
        """Запуск теста производительности"""
        print("🚀 Запуск теста производительности...")
        
        methods_to_test = [
            ("get_balance", ["ltc1q..."]),
            ("get_blockchain_info", []),
            ("estimate_fee", [3]),
            ("validate_address", ["ltc1q..."])
        ]
        
        for coin in ["LTC", "DOGE"]:
            print(f"\n🔧 Тестируем {coin}:")
            
            for method_name, args in methods_to_test:
                times = []
                successes = 0
                
                for i in range(iterations):
                    result = await self.measure_method(coin, method_name, *args)
                    
                    if result['success']:
                        times.append(result['time'])
                        successes += 1
                    
                    # Пауза между запросами
                    await asyncio.sleep(0.5)
                
                if times:
                    avg_time = statistics.mean(times)
                    min_time = min(times)
                    max_time = max(times)
                    
                    print(f"   {method_name}:")
                    print(f"     Успешно: {successes}/{iterations}")
                    print(f"     Среднее: {avg_time:.3f} сек")
                    print(f"     Минимум: {min_time:.3f} сек")
                    print(f"     Максимум: {max_time:.3f} сек")
                else:
                    print(f"   {method_name}: ❌ Все запросы неудачны")
        
        print("\n🎯 Тест производительности завершен")

async def main():
    monitor = PerformanceMonitor()
    await monitor.run_performance_test(iterations=5)

if __name__ == "__main__":
    asyncio.run(main())
📈 Производительность
Оптимизация для больших объемов:
python
# optimized_manager.py
import asyncio
from node_manager import NodeManager
from node_manager.utils.exceptions import NodeError

class OptimizedNodeManager(NodeManager):
    """Оптимизированный менеджер для больших объемов"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}
        self._cache_ttl = 300  # 5 минут
        
    async def get_balance_cached(self, coin, address, force_refresh=False):
        """Кэширование балансов"""
        cache_key = f"{coin}:{address}:balance"
        
        # Проверяем кэш
        if not force_refresh and cache_key in self._cache:
            cache_data = self._cache[cache_key]
            if time.time() - cache_data['timestamp'] < self._cache_ttl:
                return cache_data['data']
        
        # Получаем свежие данные
        node = await self.get_node(coin)
        balance = await node.get_balance(address)
        
        # Сохраняем в кэш
        self._cache[cache_key] = {
            'data': balance,
            'timestamp': time.time()
        }
        
        # Очистка старого кэша
        self._clean_old_cache()
        
        return balance
    
    async def batch_monitor_addresses(self, coin, addresses):
        """Пакетное добавление адресов в мониторинг"""
        node = await self.get_node(coin)
        
        # Валидация всех адресов за один раз
        validation_tasks = []
        for address in addresses:
            validation_tasks.append(node.validate_address(address))
        
        validation_results = await asyncio.gather(*validation_tasks)
        
        # Добавляем только валидные адреса
        valid_addresses = []
        for address, validation in zip(addresses, validation_results):
            if validation.get('is_valid'):
                valid_addresses.append(address)
        
        # Пакетная подписка (если API поддерживает)
        if valid_addresses:
            # Здесь должна быть реализация пакетной подписки
            # В зависимости от возможностей Nownodes API
            pass
        
        return {
            'total': len(addresses),
            'valid': len(valid_addresses),
            'invalid': len(addresses) - len(valid_addresses),
            'valid_addresses': valid_addresses
        }
    
    def _clean_old_cache(self):
        """Очистка старого кэша"""
        current_time = time.time()
        keys_to_delete = []
        
        for key, data in self._cache.items():
            if current_time - data['timestamp'] > self._cache_ttl * 2:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self._cache[key]
    
    async def health_check_all(self):
        """Проверка здоровья всех нод параллельно"""
        tasks = []
        
        for coin in self._get_enabled_coins():
            tasks.append(self._check_node_health(coin))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_status = {}
        for coin, result in zip(self._get_enabled_coins(), results):
            if isinstance(result, Exception):
                health_status[coin] = {
                    'healthy': False,
                    'error': str(result)
                }
            else:
                health_status[coin] = {
                    'healthy': True,
                    'block_height': result.get('blocks', 0)
                }
        
        return health_status
    
    async def _check_node_health(self, coin):
        """Проверка здоровья конкретной ноды"""
        try:
            node = await self.get_node(coin)
            info = await node.get_blockchain_info()
            return info
        except Exception as e:
            raise Exception(f"Node {coin} health check failed: {e}")

# Использование оптимизированного менеджера
async def main():
    manager = OptimizedNodeManager()
    
    # Пакетная обработка адресов
    addresses = ["ltc1q..."] * 100  # 100 адресов
    result = await manager.batch_monitor_addresses("LTC", addresses)
    print(f"Обработано {result['total']} адресов, {result['valid']} валидных")
    
    # Кэшированные запросы
    balance = await manager.get_balance_cached("LTC", "ltc1q...")
    print(f"Баланс: {balance['total']}")
    
    # Параллельная проверка здоровья
    health = await manager.health_check_all()
    for coin, status in health.items():
        print(f"{coin}: {'✅' if status['healthy'] else '❌'}")

asyncio.run(main())
🤝 Вклад в проект
Установка для разработки:
bash
# Клонируйте репозиторий
git clone https://github.com/yourusername/node-manager.git
cd node-manager

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Установите модуль в режиме разработки
pip install -e .
Запуск тестов:
bash
# Запуск всех тестов
pytest tests/

# Запуск с покрытием кода
pytest tests/ --cov=node_manager --cov-report=html

# Запуск конкретного теста
pytest tests/test_litecoin_node.py -v

# Тестирование с разными версиями Python
tox
Стиль кода:
bash
# Автоформатирование кода
black node_manager/

# Проверка стиля
flake8 node_manager/

# Проверка типов
mypy node_manager/

# Сортировка импортов
isort node_manager/
Процесс внесения изменений:
Форкните репозиторий

Создайте ветку для вашей функции (git checkout -b feature/amazing-feature)

Закоммитьте изменения (git commit -m 'Add amazing feature')

Запушьте в ветку (git push origin feature/amazing-feature)

Откройте Pull Request

Структура тестов:
text
tests/
├── __init__.py
├── conftest.py              # Фикстуры
├── test_base_node.py       # Тесты базового класса
├── test_litecoin_node.py   # Тесты Litecoin
├── test_dogecoin_node.py   # Тесты Dogecoin
├── test_node_factory.py    # Тесты фабрики
├── test_monitor.py         # Тесты мониторинга
├── test_collector.py       # Тесты сборщика
├── test_manager.py         # Тесты менеджера
└── integration/            # Интеграционные тесты
    ├── test_connection.py
    └── test_transactions.py
Пример теста:
python
# tests/test_litecoin_node.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from node_manager.core.litecoin import LitecoinNode

class TestLitecoinNode:
    @pytest.fixture
    def node(self):
        """Фикстура для создания тестовой ноды"""
        return LitecoinNode(
            coin_type="LTC",
            api_key="test_key",
            blockbook_url="https://test.com",
            rpc_url="https://test.com"
        )
    
    @pytest.mark.asyncio
    async def test_connect_success(self, node):
        """Тест успешного подключения"""
        # Мокаем клиентов
        node.rpc_client = AsyncMock()
        node.rpc_client.call.return_value = {'result': {'blocks': 1000}}
        
        node.blockbook_client = AsyncMock()
        node.blockbook_client.get_blockbook_info.return_value = {}
        
        # Тестируем подключение
        result = await node.connect()
        
        assert result is True
        assert node.is_connected() is True
    
    @pytest.mark.asyncio
    async def test_get_balance(self, node):
        """Тест получения баланса"""
        # Мокаем blockbook_client
        node.blockbook_client = AsyncMock()
        node.blockbook_client.get_address_info.return_value = {
            'balance': 100000000,  # 1 LTC в сатоши
            'unconfirmedBalance': 50000000,  # 0.5 LTC
            'totalReceived': 150000000,
            'txs': 5
        }
        
        # Тестируем получение баланса
        balance = await node.get_balance("ltc1qtest")
        
        assert balance['address'] == "ltc1qtest"
        assert balance['confirmed'] == 1.0  # 1 LTC
        assert balance['unconfirmed'] == 0.5  # 0.5 LTC
        assert balance['total'] == 1.5
        assert balance['transaction_count'] == 5
    
    @pytest.mark.asyncio
    async def test_validate_address(self, node):
        """Тест валидации адреса"""
        # Тестируем валидный адрес
        node.blockbook_client = AsyncMock()
        node.blockbook_client.get_address_info.return_value = {}
        
        validation = await node.validate_address("ltc1qtestaddress")
        
        assert validation['is_valid'] is True
        assert validation['address'] == "ltc1qtestaddress"
📄 Лицензия
Этот проект распространяется под лицензией MIT. См. файл LICENSE для получения подробной информации.

Основные положения:
Разрешено:

Использовать в коммерческих целях

Модифицировать и распространять

Использовать в частных проектах

Распространять с указанием авторства

Требуется:

Сохранять уведомление об авторских правах и лицензии

Указывать изменения в коде

Запрещено:

Отказываться от ответственности автора

Использовать товарные знаки автора

Авторские права:
text
Copyright (c) 2024 Node Manager Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
Вкладчики:
Основной разработчик: Ваше Имя

Контрибьюторы: Список вкладчиков

Поддержка проекта:
Если вы нашли этот проект полезным, рассмотрите возможность:

⭐ Поставить звезду на GitHub

🐛 Сообщить об ошибке через Issues

💡 Предложить улучшение через Pull Requests

☕ Поддержать разработчика кофе

<div align="center">
Спасибо за использование Node Manager! 🚀

Если у вас есть вопросы или нужна помощь, создайте Issue на GitHub.

Документация |
Примеры |
Issues

</div>
Теперь предоставлю полный код всех файлов модуля.
