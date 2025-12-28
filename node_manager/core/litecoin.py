"""
Реализация ноды Litecoin
"""
import logging
from typing import Dict, List, Any, Union
from decimal import Decimal
from .base_node import BaseNode

logger = logging.getLogger(__name__)

class LitecoinNode(BaseNode):
    """Нода Litecoin"""
    
    def __init__(self, **kwargs):
        # Установка параметров для Litecoin
        kwargs.setdefault('coin_type', 'LTC')
        kwargs.setdefault('coin_name', 'Litecoin')
        kwargs.setdefault('decimals', 8)
        
        # URL по умолчанию для Nownodes
        if not kwargs.get('blockbook_url'):
            kwargs['blockbook_url'] = 'https://ltcbook.nownodes.io'
        if not kwargs.get('rpc_url'):
            kwargs['rpc_url'] = 'https://ltc.nownodes.io'
        
        super().__init__(**kwargs)
    
    async def connect(self) -> bool:
        """Подключение к Litecoin ноде"""
        try:
            logger.info(f"Connecting to Litecoin node...")
            
            # Проверяем подключение через Blockbook
            if self.blockbook_client:
                info = await self.blockbook_client.get_blockbook_info()
                if 'error' in info:
                    logger.warning(f"Blockbook connection failed: {info['error']}")
            
            # Проверяем подключение через RPC
            if self.rpc_client:
                result = await self.rpc_client.call("getblockchaininfo", [])
                if 'error' in result:
                    logger.warning(f"RPC connection failed: {result['error']}")
            
            self._connected = True
            logger.info(f"Connected to Litecoin node (network: {self.network})")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Litecoin node: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Отключение от ноды"""
        self._connected = False
        logger.info("Disconnected from Litecoin node")
        return True
    
    async def get_balance(self, address: str) -> Dict[str, Any]:
        """Получить баланс адреса Litecoin"""
        try:
            if not self.blockbook_client:
                return {'error': 'Blockbook client not available'}
            
            info = await self.blockbook_client.get_address_info(address)
            
            if 'error' in info:
                return info
            
            confirmed = self.satoshi_to_coin(info.get('balance', 0))
            unconfirmed = self.satoshi_to_coin(info.get('unconfirmedBalance', 0))
            total_received = self.satoshi_to_coin(info.get('totalReceived', 0))
            
            return {
                'address': address,
                'confirmed': confirmed,
                'unconfirmed': unconfirmed,
                'total': confirmed + unconfirmed,
                'total_received': total_received,
                'transaction_count': info.get('txs', 0),
                'coin': 'LTC'
            }
            
        except Exception as e:
            logger.error(f"Error getting LTC balance: {e}")
            return {'error': str(e)}
    
    async def get_address_info(self, address: str) -> Dict[str, Any]:
        """Получить информацию об адресе Litecoin"""
        try:
            if not self.blockbook_client:
                return {'error': 'Blockbook client not available'}
            
            info = await self.blockbook_client.get_detailed_address_info(address)
            
            if 'error' in info:
                return info
            
            # Форматируем транзакции
            transactions = []
            for tx in info.get('transactions', [])[:20]:  # Ограничиваем
                tx_data = {
                    'txid': tx.get('txid'),
                    'confirmations': tx.get('confirmations', 0),
                    'block_height': tx.get('blockHeight'),
                    'timestamp': tx.get('blockTime'),
                    'value': self.satoshi_to_coin(tx.get('value', 0))
                }
                transactions.append(tx_data)
            
            return {
                'address': address,
                'balance': self.satoshi_to_coin(info.get('balance', 0)),
                'unconfirmed_balance': self.satoshi_to_coin(info.get('unconfirmedBalance', 0)),
                'total_received': self.satoshi_to_coin(info.get('totalReceived', 0)),
                'total_sent': self.satoshi_to_coin(info.get('totalSent', 0)),
                'transaction_count': info.get('txs', 0),
                'transactions': transactions,
                'utxo_count': len(info.get('txids', [])),
                'coin': 'LTC'
            }
            
        except Exception as e:
            logger.error(f"Error getting LTC address info: {e}")
            return {'error': str(e)}
    
    async def get_transaction(self, txid: str) -> Dict[str, Any]:
        """Получить информацию о транзакции Litecoin"""
        try:
            # Пробуем сначала Blockbook
            if self.blockbook_client:
                tx_info = await self.blockbook_client.get_transaction(txid)
                if 'error' not in tx_info:
                    return self._format_transaction(tx_info)
            
            # Fallback на RPC
            if self.rpc_client:
                result = await self.rpc_client.call("getrawtransaction", [txid, True])
                if 'error' not in result:
                    return self._format_transaction(result.get('result', {}))
            
            return {'error': 'Failed to get transaction info'}
            
        except Exception as e:
            logger.error(f"Error getting LTC transaction: {e}")
            return {'error': str(e)}
    
    async def get_address_utxos(self, address: str) -> List[Dict[str, Any]]:
        """Получить UTXO адреса Litecoin"""
        try:
            if not self.blockbook_client:
                return []
            
            utxos = await self.blockbook_client.get_address_utxos(address)
            
            if isinstance(utxos, dict) and 'error' in utxos:
                return []
            
            formatted_utxos = []
            for utxo in utxos:
                formatted_utxos.append({
                    'txid': utxo.get('txid'),
                    'vout': utxo.get('vout', 0),
                    'address': address,
                    'amount': self.satoshi_to_coin(utxo.get('value', 0)),
                    'confirmations': utxo.get('confirmations', 0),
                    'script_pub_key': utxo.get('scriptPubKey', ''),
                    'coin': 'LTC'
                })
            
            return formatted_utxos
            
        except Exception as e:
            logger.error(f"Error getting LTC UTXOs: {e}")
            return []
    
    async def send_transaction(self, raw_tx_hex: str) -> str:
        """Отправить транзакцию Litecoin"""
        try:
            if not self.rpc_client:
                raise Exception("RPC client not available")
            
            result = await self.rpc_client.call("sendrawtransaction", [raw_tx_hex])
            
            if 'error' in result:
                raise Exception(f"RPC error: {result['error']}")
            
            txid = result.get('result')
            logger.info(f"LTC transaction sent: {txid}")
            return txid
            
        except Exception as e:
            logger.error(f"Error sending LTC transaction: {e}")
            raise
    
    async def create_raw_transaction(self, 
                                   inputs: List[Dict], 
                                   outputs: Dict[str, Union[float, Decimal]]) -> str:
        """Создать сырую транзакцию Litecoin"""
        try:
            if not self.rpc_client:
                raise Exception("RPC client not available")
            
            # Форматируем выходы
            formatted_outputs = {}
            for address, amount in outputs.items():
                formatted_outputs[address] = float(amount)
            
            result = await self.rpc_client.call("createrawtransaction", [inputs, formatted_outputs])
            
            if 'error' in result:
                raise Exception(f"RPC error: {result['error']}")
            
            return result.get('result', '')
            
        except Exception as e:
            logger.error(f"Error creating LTC raw transaction: {e}")
            raise
    
    async def sign_raw_transaction(self, 
                                 raw_tx_hex: str, 
                                 private_keys: List[str] = None) -> Dict[str, Any]:
        """Подписать сырую транзакцию Litecoin"""
        try:
            if not self.rpc_client:
                raise Exception("RPC client not available")
            
            if private_keys is None:
                private_keys = []
            
            result = await self.rpc_client.call("signrawtransactionwithkey", [raw_tx_hex, private_keys])
            
            if 'error' in result:
                raise Exception(f"RPC error: {result['error']}")
            
            signed_data = result.get('result', {})
            
            return {
                'hex': signed_data.get('hex', ''),
                'complete': signed_data.get('complete', False),
                'errors': signed_data.get('errors', [])
            }
            
        except Exception as e:
            logger.error(f"Error signing LTC transaction: {e}")
            raise
    
    def _format_transaction(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Форматировать информацию о транзакции"""
        # Определяем сумму на основе выходов
        total_output = 0
        outputs = []
        
        for vout in tx_data.get('vout', []):
            value = vout.get('value', 0)
            if isinstance(value, (int, float)):
                amount = value
            elif isinstance(value, str):
                amount = float(value)
            else:
                amount = 0
            
            total_output += amount
            
            # Получаем адреса из выхода
            addresses = []
            if 'scriptPubKey' in vout:
                script = vout['scriptPubKey']
                if 'addresses' in script:
                    addresses = script['addresses']
                elif 'address' in script:
                    addresses = [script['address']]
            
            outputs.append({
                'value': amount,
                'addresses': addresses,
                'n': vout.get('n', 0)
            })
        
        return {
            'txid': tx_data.get('txid'),
            'hash': tx_data.get('hash'),
            'version': tx_data.get('version'),
            'size': tx_data.get('size'),
            'vsize': tx_data.get('vsize'),
            'weight': tx_data.get('weight'),
            'locktime': tx_data.get('locktime'),
            'blockhash': tx_data.get('blockhash'),
            'confirmations': tx_data.get('confirmations', 0),
            'time': tx_data.get('time'),
            'blocktime': tx_data.get('blocktime'),
            'amount': total_output,
            'fee': tx_data.get('fee', 0),
            'inputs': tx_data.get('vin', []),
            'outputs': outputs,
            'coin': 'LTC'
        }
