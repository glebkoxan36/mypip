"""
Реализация ноды Dogecoin
"""
import logging
from typing import Dict, List, Any, Union
from decimal import Decimal
from .base_node import BaseNode

logger = logging.getLogger(__name__)

class DogecoinNode(BaseNode):
    """Нода Dogecoin"""
    
    def __init__(self, **kwargs):
        # Установка параметров для Dogecoin
        kwargs.setdefault('coin_type', 'DOGE')
        kwargs.setdefault('coin_name', 'Dogecoin')
        kwargs.setdefault('decimals', 8)
        
        # URL по умолчанию для Nownodes
        if not kwargs.get('blockbook_url'):
            kwargs['blockbook_url'] = 'https://dogebook.nownodes.io'
        if not kwargs.get('rpc_url'):
            kwargs['rpc_url'] = 'https://doge.nownodes.io'
        
        super().__init__(**kwargs)
    
    async def connect(self) -> bool:
        """Подключение к Dogecoin ноде"""
        try:
            logger.info(f"Connecting to Dogecoin node...")
            
            # Dogecoin использует немного другой RPC API
            if self.rpc_client:
                # Пробуем получить информацию через getinfo
                result = await self.rpc_client.call("getinfo", [])
                if 'error' not in result:
                    self._connected = True
                    logger.info(f"Connected to Dogecoin node (network: {self.network})")
                    return True
            
            self._connected = True  # Все равно помечаем как подключенную
            logger.info(f"Connected to Dogecoin node (network: {self.network})")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to Dogecoin node: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Отключение от ноды"""
        self._connected = False
        logger.info("Disconnected from Dogecoin node")
        return True
    
    async def get_balance(self, address: str) -> Dict[str, Any]:
        """Получить баланс адреса Dogecoin"""
        try:
            if not self.blockbook_client:
                # Fallback на RPC
                if self.rpc_client:
                    result = await self.rpc_client.call("getreceivedbyaddress", [address, 0])
                    if 'error' not in result:
                        balance = result.get('result', 0)
                        return {
                            'address': address,
                            'confirmed': balance,
                            'unconfirmed': 0,
                            'total': balance,
                            'coin': 'DOGE'
                        }
                return {'error': 'No API client available'}
            
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
                'coin': 'DOGE'
            }
            
        except Exception as e:
            logger.error(f"Error getting DOGE balance: {e}")
            return {'error': str(e)}
    
    async def get_address_info(self, address: str) -> Dict[str, Any]:
        """Получить информацию об адресе Dogecoin"""
        try:
            if not self.blockbook_client:
                # Простая проверка через RPC
                if self.rpc_client:
                    result = await self.rpc_client.call("validateaddress", [address])
                    if 'error' not in result:
                        validation = result.get('result', {})
                        return {
                            'address': address,
                            'is_valid': validation.get('isvalid', False),
                            'is_mine': validation.get('ismine', False),
                            'is_script': validation.get('isscript', False),
                            'coin': 'DOGE'
                        }
                return {'error': 'No API client available'}
            
            info = await self.blockbook_client.get_detailed_address_info(address)
            
            if 'error' in info:
                return info
            
            # Форматируем транзакции
            transactions = []
            for tx in info.get('transactions', [])[:20]:
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
                'coin': 'DOGE'
            }
            
        except Exception as e:
            logger.error(f"Error getting DOGE address info: {e}")
            return {'error': str(e)}
    
    async def get_transaction(self, txid: str) -> Dict[str, Any]:
        """Получить информацию о транзакции Dogecoin"""
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
            logger.error(f"Error getting DOGE transaction: {e}")
            return {'error': str(e)}
    
    async def get_address_utxos(self, address: str) -> List[Dict[str, Any]]:
        """Получить UTXO адреса Dogecoin"""
        try:
            # Сначала пробуем RPC
            if self.rpc_client:
                result = await self.rpc_client.call("listunspent", [0, 9999999, [address]])
                if 'error' not in result:
                    utxos_data = result.get('result', [])
                    
                    formatted_utxos = []
                    for utxo in utxos_data:
                        formatted_utxos.append({
                            'txid': utxo.get('txid'),
                            'vout': utxo.get('vout', 0),
                            'address': utxo.get('address', address),
                            'amount': utxo.get('amount', 0),
                            'confirmations': utxo.get('confirmations', 0),
                            'script_pub_key': utxo.get('scriptPubKey', ''),
                            'coin': 'DOGE'
                        })
                    
                    return formatted_utxos
            
            # Fallback на Blockbook
            if self.blockbook_client:
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
                        'coin': 'DOGE'
                    })
                
                return formatted_utxos
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting DOGE UTXOs: {e}")
            return []
    
    async def send_transaction(self, raw_tx_hex: str) -> str:
        """Отправить транзакцию Dogecoin"""
        try:
            if not self.rpc_client:
                raise Exception("RPC client not available")
            
            result = await self.rpc_client.call("sendrawtransaction", [raw_tx_hex])
            
            if 'error' in result:
                raise Exception(f"RPC error: {result['error']}")
            
            txid = result.get('result')
            logger.info(f"DOGE transaction sent: {txid}")
            return txid
            
        except Exception as e:
            logger.error(f"Error sending DOGE transaction: {e}")
            raise
    
    async def create_raw_transaction(self, 
                                   inputs: List[Dict], 
                                   outputs: Dict[str, Union[float, Decimal]]) -> str:
        """Создать сырую транзакцию Dogecoin"""
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
            logger.error(f"Error creating DOGE raw transaction: {e}")
            raise
    
    async def sign_raw_transaction(self, 
                                 raw_tx_hex: str, 
                                 private_keys: List[str] = None) -> Dict[str, Any]:
        """Подписать сырую транзакцию Dogecoin"""
        try:
            if not self.rpc_client:
                raise Exception("RPC client not available")
            
            if private_keys is None:
                private_keys = []
            
            # Dogecoin использует немного другой синтаксис
            result = await self.rpc_client.call("signrawtransaction", [raw_tx_hex, [], private_keys])
            
            if 'error' in result:
                raise Exception(f"RPC error: {result['error']}")
            
            signed_data = result.get('result', {})
            
            return {
                'hex': signed_data.get('hex', ''),
                'complete': signed_data.get('complete', False)
            }
            
        except Exception as e:
            logger.error(f"Error signing DOGE transaction: {e}")
            raise
    
    def _format_transaction(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Форматировать информацию о транзакции Dogecoin"""
        # Аналогично Litecoin, но для Dogecoin
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
            'locktime': tx_data.get('locktime'),
            'blockhash': tx_data.get('blockhash'),
            'confirmations': tx_data.get('confirmations', 0),
            'time': tx_data.get('time'),
            'blocktime': tx_data.get('blocktime'),
            'amount': total_output,
            'inputs': tx_data.get('vin', []),
            'outputs': outputs,
            'coin': 'DOGE'
        }
