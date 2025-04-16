from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime, timedelta
from uuid import uuid4
from faker import Faker

# Инициализация Faker для генерации случайных данных
fake = Faker()

# Настройки генерации
BRANCH_IDS = [1, 2, 3, 4, 5]  # ID филиалов
PAYMENT_METHODS = ['cash', 'card', 'mobile']  # Способы оплаты
OPERATOR_IDS = [f"OP-{1000 + i}" for i in range(20)]  # ID операторов

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    api_version=(3, 4, 0),
    acks='all',  # Гарантированная доставка
    retries=3    # Количество попыток повторной отправки
)

def delivery_report(err, msg):
    """ Callback для отчетов о доставке сообщений """
    if err is not None:
        print(f"Message delivery failed: {err}", flush=True)
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]", flush=True)

def generate_transaction():
    """Генерация случайной транзакции"""
    transaction_time = datetime.now()
    is_return = random.random() < 0.05  # 5% вероятность возврата
    
    amount = round(random.uniform(50, 2000), 2)
    if is_return:
        amount = -abs(amount)  # Гарантируем отрицательную сумму для возврата
    
    # Генерация дополнительной информации
    additional_info = {
        "discount_applied": random.random() < 0.3,
        "loyalty_card_used": random.random() < 0.4,
        "receipt_number": fake.bothify('#####-######'),
        "items": [
            {"product_id": fake.ean(), "price": round(random.uniform(5, 500), 2), "quantity": random.randint(1, 5)}
            for _ in range(random.randint(1, 5))
        ]
    }
    
    return {
        "transaction_id": str(uuid4()),
        "branch_id": random.choice(BRANCH_IDS),
        "transaction_time": transaction_time.isoformat(),
        "amount": amount,
        "payment_method": random.choice(PAYMENT_METHODS),
        "customer_id": fake.uuid4()[:10] if random.random() < 0.7 else None,
        "items_count": sum(item['quantity'] for item in additional_info['items']),
        "is_return": is_return,
        "operator_id": random.choice(OPERATOR_IDS),
        "additional_info": additional_info
    }

topic = "transactions"  # Топик для транзакций

try:
    while True:
        # Генерация транзакции
        transaction = generate_transaction()
        
        try:
            # Отправка сообщения с callback для отслеживания доставки
            future = producer.send(
                topic, 
                value=transaction,
            ).add_callback(delivery_report)
            
            # Ожидание подтверждения (для демонстрации)
            metadata = future.get(timeout=10)
            print(f"Sent transaction {transaction['transaction_id']} for branch {transaction['branch_id']}", flush=True)
            
            # Случайный интервал между отправками (0.1-2 секунды)
            time.sleep(random.uniform(0.1, 2))
            
        except Exception as e:
            print(f"Error sending transaction: {str(e)}", flush=True)
            time.sleep(5)  # Пауза при ошибке
            
except KeyboardInterrupt:
    print("Stopping producer...", flush=True)
    
finally:
    # Завершение работы продюсера
    producer.flush()
    producer.close()