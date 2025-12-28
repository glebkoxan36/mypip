"""
Сервис для сбора средств
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)

class FundsCollector:
    """Сборщик средств на основной адрес"""
    
    def __init__(self, node, master_address: str, fee: float = 0.0001):
        """
        Args:
            node: Экземпляр ноды
            master_address: Основной адрес для сбора
            fee: Комиссия сбора
        """
        self.node = node
        self.master_address = master_address
        self.collection_fee = fee
        self.min_collection_amount = 0.001
        self.is_processing = False
        
    async def collect_from_address(self, 
                                 source_address: str, 
                                 private_key: str = None) -> Optional[Dict[str, Any]]:
        """
        Собрать средства с адреса
        
        Args:
            source_address: Адрес источника
            private_key: Приватный ключ для подписи (опционально)
        
        Returns:
            dict: Информация о сборе или None при ошибке
        """
        if self.is_processing:
            logger.warning("Collection already in progress")
            return None
        
        self.is_processing = True
        
        try:
            logger.info(f"Starting collection from {source_address}")
            
            # 1. Получаем UTXO
            utxos = await self.node.get_address_utxos(source_address)
            if not utxos:
                logger.info(f"No UTXOs found for {source_address}")
                return None
            
            # 2. Фильтруем подтвержденные UTXO
            confirmed_utxos = [u for u in utxos if u.get('confirmations', 0) >= 1]
            if not confirmed_utxos:
                logger.info(f"No confirmed UTXOs for {source_address}")
                return None
            
            # 3. Рассчитываем общую сумму
            total_amount = sum(u['amount'] for u in confirmed_utxos)
            
            # 4. Проверяем минимальную сумму
            if total_amount < self.min_collection_amount:
                logger.info(f"Insufficient amount: {total_amount:.8f} < {self.min_collection_amount}")
                return None
            
            # 5. Рассчитываем сумму для отправки (минус комиссия)
            amount_to_send = total_amount - self.collection_fee
            
            if amount_to_send <= 0:
                logger.warning("Amount to send is zero or negative")
                return None
            
            logger.info(f"Total: {total_amount:.8f}, To send: {amount_to_send:.8f}, Fee: {self.collection_fee:.8f}")
            
            # 6. Создаем транзакцию
            inputs = [{'txid': u['txid'], 'vout': u['vout']} for u in confirmed_utxos]
            outputs = {self.master_address: amount_to_send}
            
            raw_tx = await self.node.create_raw_transaction(inputs, outputs)
            
            # 7. Подписываем если есть приватный ключ
            if private_key:
                signed_tx = await self.node.sign_raw_transaction(raw_tx, [private_key])
                if not signed_tx.get('complete', False):
                    logger.error("Failed to sign transaction")
                    return None
                raw_tx = signed_tx['hex']
            
            # 8. Отправляем транзакцию
            txid = await self.node.send_transaction(raw_tx)
            
            # 9. Формируем результат
            result = {
                'success': True,
                'txid': txid,
                'from_address': source_address,
                'to_address': self.master_address,
                'amount': amount_to_send,
                'fee': self.collection_fee,
                'total': total_amount,
                'utxo_count': len(confirmed_utxos),
                'timestamp': asyncio.get_event_loop().time()
            }
            
            logger.info(f"Collection successful: {txid}")
            return result
            
        except Exception as e:
            logger.error(f"Collection error: {e}")
            return {
                'success': False,
                'error': str(e),
                'from_address': source_address
            }
        finally:
            self.is_processing = False
    
    async def collect_multiple(self, 
                             addresses: List[str], 
                             private_keys: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Собрать средства с нескольких адресов
        
        Args:
            addresses: Список адресов
            private_keys: Словарь {адрес: приватный_ключ}
        
        Returns:
            dict: Результаты сбора
        """
        if private_keys is None:
            private_keys = {}
        
        results = {
            'total': len(addresses),
            'successful': 0,
            'failed': 0,
            'collections': [],
            'total_collected': 0,
            'total_fees': 0
        }
        
        for address in addresses:
            try:
                private_key = private_keys.get(address)
                result = await self.collect_from_address(address, private_key)
                
                if result and result.get('success'):
                    results['successful'] += 1
                    results['total_collected'] += result.get('amount', 0)
                    results['total_fees'] += result.get('fee', 0)
                else:
                    results['failed'] += 1
                
                if result:
                    results['collections'].append(result)
                
                # Задержка между сборами
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error collecting from {address}: {e}")
                results['failed'] += 1
                results['collections'].append({
                    'success': False,
                    'from_address': address,
                    'error': str(e)
                })
        
        return results
    
    async def estimate_collection(self, address: str) -> Dict[str, Any]:
        """
        Оценить возможный сбор с адреса
        
        Args:
            address: Адрес для оценки
        
        Returns:
            dict: Информация об оценке
        """
        try:
            utxos = await self.node.get_address_utxos(address)
            
            if not utxos:
                return {
                    'can_collect': False,
                    'reason': 'No UTXOs',
                    'address': address
                }
            
            confirmed_utxos = [u for u in utxos if u.get('confirmations', 0) >= 1]
            
            if not confirmed_utxos:
                return {
                    'can_collect': False,
                    'reason': 'No confirmed UTXOs',
                    'address': address
                }
            
            total_amount = sum(u['amount'] for u in confirmed_utxos)
            amount_to_send = total_amount - self.collection_fee
            
            can_collect = amount_to_send > 0 and total_amount >= self.min_collection_amount
            
            return {
                'can_collect': can_collect,
                'address': address,
                'total_amount': total_amount,
                'amount_to_send': amount_to_send if can_collect else 0,
                'fee': self.collection_fee,
                'utxo_count': len(confirmed_utxos),
                'min_amount': self.min_collection_amount,
                'reason': 'Sufficient funds' if can_collect else 'Insufficient funds'
            }
            
        except Exception as e:
            logger.error(f"Estimation error for {address}: {e}")
            return {
                'can_collect': False,
                'address': address,
                'error': str(e)
            }
    
    def set_fee(self, fee: float):
        """Установить комиссию сбора"""
        if fee < 0:
            raise ValueError("Fee cannot be negative")
        self.collection_fee = fee
        logger.info(f"Collection fee set to {fee}")
    
    def set_min_amount(self, min_amount: float):
        """Установить минимальную сумму для сбора"""
        if min_amount < 0:
            raise ValueError("Minimum amount cannot be negative")
        self.min_collection_amount = min_amount
        logger.info(f"Minimum collection amount set to {min_amount}")
