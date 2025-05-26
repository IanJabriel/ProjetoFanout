# subscriber_1/receive_pedidos.py
import pika
import json

url ="amqps://lmekinzw:2gdlEmnCEF_sOkquhyQiNiKBm_9WP3Mt@jackal.rmq.cloudamqp.com/lmekinzw"
#url = "amqps://mhirgjrw:HPdYkuZmViXz4dQU03Z1N7j3v6I3jFP5@shark.rmq.cloudamqp.com/mhirgjrw"
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

exchange_name ="promocool_exchange_fanout3" 
#'teste_pedidos_exchange'
queue_name = 'fila_promocool_1'

channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', durable=True)
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange=exchange_name, queue=queue_name)

def callback(ch, method, properties, body):
    pedido = json.loads(body)
    print(f"[Subscriber 1] Pedido recebido: {pedido}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue=queue_name, on_message_callback=callback)
print("[Subscriber 1] Esperando mensagens...")
channel.start_consuming()
