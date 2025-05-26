# subscriber_3/receive_promocoes.py
import pika
import json
import requests
from datetime import datetime

# Configurações
RABBITMQ_URL = "amqps://lmekinzw:2gdlEmnCEF_sOkquhyQiNiKBm_9WP3Mt@jackal.rmq.cloudamqp.com/lmekinzw"
EXCHANGE_NAME = "promocool_exchange_fanout3"
QUEUE_NAME = "fila_promocool_3"
DLX_EXCHANGE = "promocool_dlx"
API_URL = "http://127.0.0.1:8000/receberPromocao/"

def setup_rabbitmq():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='fanout', durable=True)
    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
        arguments={
            'x-dead-letter-exchange': DLX_EXCHANGE,
            'x-dead-letter-routing-key': 'dlq'
        }
    )
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME)
    
    return connection, channel

def validate_message(message):
    """Valida a estrutura da mensagem do publisher"""
    if 'marca' not in message or not isinstance(message['marca'], str):
        return "Campo 'marca' inválido ou faltando"
    
    if 'produtos' not in message or not isinstance(message['produtos'], list):
        return "Campo 'produtos' inválido ou faltando"
    
    for produto in message['produtos']:
        error = validate_produto(produto)
        if error:
            return error
    
    return None

def validate_produto(produto):
    """Valida um produto individual"""
    campos_obrigatorios = {
        'id': int,
        'nome': str,
        'porcentagem': int,
        'dataInicio': str,
        'dataFim': str
    }
    
    for campo, tipo in campos_obrigatorios.items():
        if campo not in produto:
            return f"Campo '{campo}' faltando no produto"
        if not isinstance(produto[campo], tipo):
            return f"Campo '{campo}' deve ser {tipo.__name__}"
    
    if produto['porcentagem'] > 100:
        return "Porcentagem não pode ser > 100%"
    
    try:
        datetime.fromisoformat(produto['dataInicio'].replace('Z', ''))
        datetime.fromisoformat(produto['dataFim'].replace('Z', ''))
    except ValueError:
        return "Formato de data inválido. Use 'YYYY-MM-DDTHH:MM:SSZ'"
    
    return None

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(json.dumps(message, indent=2))
        
        # Validação local
        if error := validate_message(message):
            print(f"Erro na validação: {error}")
            properties.headers = {'x-rejection-reason': error}
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        
        # Prepara payload no formato EXATO que a API espera
        payload = {
            "marca": message["marca"],
            "produtos": []
        }

        for produto in message["produtos"]:
            payload["produtos"].append({
                "id": produto["id"],
                "nome": produto["nome"],
                "preco": produto["preco"],
                "porcentagem": produto["porcentagem"],
                "dataInicio": produto["dataInicio"],
                "dataFim": produto["dataFim"]
            })
        
        print("Enviando para API")        
        response = requests.post(API_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("Mensagem processada com sucesso")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            error_msg = f"Erro na API: {response.status_code} - {response.text[:200]}"
            print(f"{error_msg}")
            properties.headers = {'x-rejection-reason': error_msg}
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
    except KeyError as e:
        error_msg = f"Campo faltando: {str(e)}"
        print(f"{error_msg}")
        properties.headers = {'x-rejection-reason': error_msg}
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}"
        print(f"{error_msg}")
        properties.headers = {'x-rejection-reason': error_msg}
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    print("Iniciando subscriber...")
    connection, channel = setup_rabbitmq()
    
    try:
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=callback,
            auto_ack=False
        )
        print("Aguardando mensagens...")
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nEncerrando subscriber...")
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == "__main__":
    main()