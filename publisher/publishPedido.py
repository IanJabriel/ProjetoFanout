import pika
import json
from datetime import datetime, timedelta

# Configuração da conexão com o RabbitMQ
connection_url = "amqps://lmekinzw:2gdlEmnCEF_sOkquhyQiNiKBm_9WP3Mt@jackal.rmq.cloudamqp.com/lmekinzw"
params = pika.URLParameters(connection_url)
connection = pika.BlockingConnection(params)

channel = connection.channel()
exchange_name = "promocool_exchange_fanout3"

channel.exchange_declare(
    exchange=exchange_name,
    exchange_type='fanout',
    durable=True)

mensagem = {
    "marca": "TESTE",
    "produtos": [
        {
            "id": 1,
            "nome": "TESTE - produto",
            "preco": 19.99,
            "porcentagem": 20,
            "dataInicio": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "dataFim": (datetime.utcnow() + timedelta(days=15)).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    ]
}

mensagem_json = json.dumps(mensagem)

channel.basic_publish(
    exchange=exchange_name,
    routing_key='',
    body=mensagem_json.encode('utf-8'),
    properties=pika.BasicProperties(delivery_mode=2)
)

print(f"[{datetime.now()}] Mensagem Promocao publicada via Fanout:")
print(mensagem_json)
print("\nMensagem enviada para TODOS os consumidores vinculados ao exchange!")

connection.close()