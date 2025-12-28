"""
Командный интерфейс для Node Manager
"""

import argparse
import asyncio
import sys
import os
import json
import yaml
from datetime import datetime
from .node_manager import NodeConfig, create_node_manager


def generate_config():
    """Генерация шаблона конфигурации"""
    try:
        NodeConfig.generate_config_template()
        print("✅ Configuration templates generated:")
        print(f"   - {NodeConfig.DEFAULT_CONFIG_PATH}")
        print(f"   - {NodeConfig.DEFAULT_ENV_PATH}")
        print("\n📝 Edit these files with your settings before running.")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


async def show_status():
    """Показать статус нод"""
    try:
        manager = await create_node_manager(auto_start=False)
        stats = await manager.get_stats()
        
        print("\n📊 Node Manager Status")
        print("=" * 50)
        
        print(f"Enabled Coins: {', '.join(stats['enabled_coins'])}")
        print(f"Connected Nodes: {stats['total_nodes']}")
        print(f"Active Monitors: {stats['total_monitors']}")
        print(f"Running Collections: {'Yes' if stats['is_running'] else 'No'}")
        
        if stats['nodes']:
            print("\n📡 Node Details:")
            for coin, info in stats['nodes'].items():
                status = "✅" if info.get('connected') else "❌"
                print(f"  {status} {coin}: ", end="")
                if info.get('connected'):
                    print(f"Block {info.get('block_height', 0)} on {info.get('network')}")
                else:
                    print(f"Error: {info.get('error', 'Unknown')}")
        
        await manager.stop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


async def test_connection(coin: str = None):
    """Тестирование подключения к нодам"""
    try:
        manager = await create_node_manager(auto_start=False)
        
        if coin:
            coins_to_test = [coin.upper()]
        else:
            coins_to_test = manager.get_enabled_coins()
        
        print(f"\n🔍 Testing connection to {len(coins_to_test)} node(s)...")
        
        success_count = 0
        for coin_type in coins_to_test:
            print(f"\n📡 {coin_type}: ", end="")
            try:
                node = await manager.get_node(coin_type)
                info = await node.get_blockchain_info()
                
                if 'error' in info:
                    print(f"❌ Error: {info['error'][:50]}...")
                else:
                    print(f"✅ Connected (Block: {info.get('blocks', 0)})")
                    success_count += 1
                
            except Exception as e:
                print(f"❌ Failed: {e}")
        
        print(f"\n🎯 Summary: {success_count}/{len(coins_to_test)} nodes connected successfully")
        
        await manager.stop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def update_api_key(new_key: str):
    """Обновление API ключа"""
    try:
        NodeConfig.update_api_key(new_key)
        print(f"✅ API key updated successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


async def show_config():
    """Показать текущую конфигурацию"""
    try:
        config = NodeConfig.load_config()
        
        print("\n⚙️ Current Configuration")
        print("=" * 50)
        
        # Показываем только безопасные части
        safe_config = config.copy()
        
        # Маскируем чувствительные данные
        if 'nownodes' in safe_config and 'api_key' in safe_config['nownodes']:
            api_key = safe_config['nownodes']['api_key']
            if api_key and len(api_key) > 8:
                safe_config['nownodes']['api_key'] = f"{api_key[:4]}...{api_key[-4:]}"
        
        for coin, coin_config in safe_config.get('coins', {}).items():
            if 'master_address' in coin_config:
                addr = coin_config['master_address']
                if addr and len(addr) > 10:
                    coin_config['master_address'] = f"{addr[:6]}...{addr[-4:]}"
        
        print(json.dumps(safe_config, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


async def check_balance(coin: str, address: str):
    """Проверка баланса адреса"""
    try:
        manager = await create_node_manager(auto_start=False)
        
        print(f"\n💰 Checking balance for {coin}:{address}")
        print("=" * 50)
        
        try:
            node = await manager.get_node(coin.upper())
            balance = await node.get_balance(address)
            
            if 'error' in balance:
                print(f"❌ Error: {balance['error']}")
            else:
                print(f"Address: {balance['address']}")
                print(f"Confirmed: {balance.get('confirmed', 0):.8f} {coin}")
                print(f"Unconfirmed: {balance.get('unconfirmed', 0):.8f} {coin}")
                print(f"Total: {balance.get('total', 0):.8f} {coin}")
                print(f"Transactions: {balance.get('transaction_count', 0)}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        await manager.stop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


async def monitor_address(coin: str, address: str):
    """Добавление адреса в мониторинг"""
    try:
        manager = await create_node_manager(auto_start=True)
        
        print(f"\n👁️ Adding {address} to monitoring for {coin}")
        print("=" * 50)
        
        try:
            await manager.monitor_address(coin.upper(), address)
            print(f"✅ Address added to monitoring")
            print(f"\n📡 Monitoring is now active. Press Ctrl+C to stop.")
            
            # Бесконечный цикл для поддержания работы
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping monitoring...")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        await manager.stop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Основная функция CLI"""
    parser = argparse.ArgumentParser(
        description='Node Manager CLI - Управление криптовалютными нодами',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  node-manager init              # Генерация конфигурационных файлов
  node-manager status           # Показать статус нод
  node-manager test             # Тестирование подключения
  node-manager test --coin LTC  # Тестирование конкретной ноды
  node-manager update-key YOUR_KEY  # Обновление API ключа
  node-manager config           # Показать текущую конфигурацию
  node-manager balance LTC ltc1q...  # Проверить баланс
  node-manager monitor LTC ltc1q...  # Мониторинг адреса
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    
    # Команда init
    subparsers.add_parser('init', help='Генерация шаблона конфигурации')
    
    # Команда status
    subparsers.add_parser('status', help='Показать статус всех нод')
    
    # Команда test
    test_parser = subparsers.add_parser('test', help='Тестирование подключения')
    test_parser.add_argument('--coin', help='Тестировать конкретную монету')
    
    # Команда update-key
    key_parser = subparsers.add_parser('update-key', help='Обновление API ключа')
    key_parser.add_argument('key', help='Новый API ключ')
    
    # Команда config
    subparsers.add_parser('config', help='Показать текущую конфигурацию')
    
    # Команда balance
    balance_parser = subparsers.add_parser('balance', help='Проверка баланса адреса')
    balance_parser.add_argument('coin', help='Тип монеты (LTC, DOGE, BTC)')
    balance_parser.add_argument('address', help='Адрес для проверки')
    
    # Команда monitor
    monitor_parser = subparsers.add_parser('monitor', help='Мониторинг адреса')
    monitor_parser.add_argument('coin', help='Тип монеты (LTC, DOGE, BTC)')
    monitor_parser.add_argument('address', help='Адрес для мониторинга')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'init':
        generate_config()
    
    elif args.command == 'status':
        asyncio.run(show_status())
    
    elif args.command == 'test':
        asyncio.run(test_connection(args.coin))
    
    elif args.command == 'update-key':
        update_api_key(args.key)
    
    elif args.command == 'config':
        asyncio.run(show_config())
    
    elif args.command == 'balance':
        asyncio.run(check_balance(args.coin, args.address))
    
    elif args.command == 'monitor':
        asyncio.run(monitor_address(args.coin, args.address))


if __name__ == "__main__":
    main()
