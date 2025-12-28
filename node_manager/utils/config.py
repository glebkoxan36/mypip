"""
Утилиты для работы с конфигурацией
"""
import os
import yaml
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Загрузка конфигурации из файла
    
    Args:
        config_path (str): Путь к конфигурационному файлу
    
    Returns:
        dict: Конфигурация
    """
    # Проверяем несколько возможных мест
    possible_paths = [
        config_path,
        'config.yaml',
        'config.yml',
        'config.json',
        os.path.join(os.path.dirname(__file__), '../../config.yaml')
    ]
    
    for path in possible_paths:
        if not path:
            continue
        
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    if path.endswith('.json'):
                        config = json.load(f)
                    else:
                        config = yaml.safe_load(f)
                
                # Заменяем переменные окружения
                config = _replace_env_vars(config)
                
                print(f"Loaded config from {path}")
                return config
            except Exception as e:
                print(f"Error loading config from {path}: {e}")
    
    # Конфигурация по умолчанию
    return get_default_config()

def get_coin_config(coin_type: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Получить конфигурацию для конкретной монеты
    
    Args:
        coin_type (str): Тип монеты
        config (dict): Общая конфигурация
    
    Returns:
        dict: Конфигурация монеты
    """
    if config is None:
        config = load_config()
    
    coin_type = coin_type.upper()
    
    # Ищем конфигурацию монеты
    coins_config = config.get('coins', {})
    if coin_type in coins_config:
        return coins_config[coin_type]
    
    # Конфигурация по умолчанию
    return get_default_coin_config(coin_type)

def get_default_config() -> Dict[str, Any]:
    """Конфигурация по умолчанию"""
    return {
        'coins': {
            'LTC': get_default_coin_config('LTC'),
            'DOGE': get_default_coin_config('DOGE'),
            'BTC': get_default_coin_config('BTC')
        },
        'connection': {
            'timeout': 30,
            'retry_attempts': 3,
            'retry_delay': 5
        },
        'websocket': {
            'ping_interval': 30,
            'reconnect_attempts': 10
        },
        'monitoring': {
            'check_interval': 60,
            'batch_size': 10
        }
    }

def get_default_coin_config(coin_type: str) -> Dict[str, Any]:
    """Конфигурация монеты по умолчанию"""
    coin_type = coin_type.upper()
    
    configs = {
        'LTC': {
            'api_key': os.getenv('LTC_NOWNODES_API_KEY', ''),
            'blockbook_url': 'https://ltcbook.nownodes.io',
            'rpc_url': 'https://ltc.nownodes.io',
            'network': 'mainnet',
            'decimals': 8,
            'coin_symbol': 'LTC',
            'coin_name': 'Litecoin',
            'min_collection_amount': 0.001,
            'collection_fee': 0.0001
        },
        'DOGE': {
            'api_key': os.getenv('DOGE_NOWNODES_API_KEY', ''),
            'blockbook_url': 'https://dogebook.nownodes.io',
            'rpc_url': 'https://doge.nownodes.io',
            'network': 'mainnet',
            'decimals': 8,
            'coin_symbol': 'DOGE',
            'coin_name': 'Dogecoin',
            'min_collection_amount': 10.0,
            'collection_fee': 1.0
        },
        'BTC': {
            'api_key': os.getenv('BTC_NOWNODES_API_KEY', ''),
            'blockbook_url': 'https://btcbook.nownodes.io',
            'rpc_url': 'https://btc.nownodes.io',
            'network': 'mainnet',
            'decimals': 8,
            'coin_symbol': 'BTC',
            'coin_name': 'Bitcoin',
            'min_collection_amount': 0.0001,
            'collection_fee': 0.00001
        }
    }
    
    return configs.get(coin_type, {})

def _replace_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Замена переменных окружения в конфиге"""
    import re
    
    def replace(obj):
        if isinstance(obj, str):
            # Заменяем ${VAR_NAME}
            match = re.search(r'\${(\w+)}', obj)
            if match:
                var_name = match.group(1)
                env_value = os.getenv(var_name, '')
                return obj.replace(f'${{{var_name}}}', env_value)
            return obj
        elif isinstance(obj, dict):
            return {k: replace(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace(item) for item in obj]
        else:
            return obj
    
    return replace(config)

def save_config(config: Dict[str, Any], config_path: str = 'config.yaml'):
    """
    Сохранение конфигурации в файл
    
    Args:
        config (dict): Конфигурация
        config_path (str): Путь для сохранения
    """
    try:
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if config_path.endswith('.json'):
                json.dump(config, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"Config saved to {config_path}")
        
    except Exception as e:
        print(f"Error saving config: {e}")
