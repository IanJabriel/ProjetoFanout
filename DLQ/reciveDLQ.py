import pika
import json
from pprint import pprint

url = "amqps://lmekinzw:2gdlEmnCEF_sOkquhyQiNiKBm_9WP3Mt@jackal.rmq.cloudamqp.com/lmekinzw"
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

dlx_exchange = "promocool_dlx"
dlq_queue = "fila_promocool_dlq"

channel.exchange_declare(exchange=dlx_exchange, exchange_type='direct', durable=True)
channel.queue_declare(queue=dlq_queue, durable=True)
channel.queue_bind(exchange=dlx_exchange, queue=dlq_queue, routing_key='dlq')

def callback(ch, method, properties, body):
    try:
        mensagem = json.loads(body)
        print("\n--- Mensagem Rejeitada na DLQ ---")
        pprint(mensagem, indent=2)
        
        if properties.headers and 'x-death' in properties.headers:
            motivo = properties.headers['x-death'][0].get('reason', 'Motivo desconhecido')
            print(f"\nMotivo: {motivo}")
        
    except json.JSONDecodeError:
        print(f"\nMensagem corrompida: {body.decode()}")

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=dlq_queue, on_message_callback=callback)
print("\n[DLQ Monitor] Pronto para receber mensagens rejeitadas. Ctrl+C para sair")
channel.start_consuming()