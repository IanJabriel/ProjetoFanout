# subscriber_2/receive_promocoes.py
import pika
import json
import requests
import time
from datetime import datetime

# Configurações
RABBITMQ_URL = "amqps://lmekinzw:2gdlEmnCEF_sOkquhyQiNiKBm_9WP3Mt@jackal.rmq.cloudamqp.com/lmekinzw"
EXCHANGE_NAME = "promocool_exchange_fanout3"
QUEUE_NAME = "fila_promocool_3"
DLX_EXCHANGE = "promocool_dlx"
API_URL = "http://127.0.0.1:8000/api/receberPromocao/" 

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
    
    try:
        datetime.fromisoformat(produto['dataInicio'].replace('Z', ''))
        datetime.fromisoformat(produto['dataFim'].replace('Z', ''))
    except ValueError:
        return "Formato de data inválido. Use 'YYYY-MM-DDTHH:MM:SSZ'"
    
    return None

def callback(ch, method, properties, body):
    time.sleep(1.5)
    try:
        message = json.loads(body)
        print(json.dumps(message, indent=2))
    
        # Validação local
        if error := validate_message(message):
            print(f"Erro na validação: {error}")
            
            # Gera log para erros de validação
            with open("erros.log", "a", encoding='utf-8') as log:
                log.write(f"[{datetime.now()}] Erro de Validação\n")
                log.write(f"Mensagem: {json.dumps(message, indent=2)}\n")
                log.write(f"Erro: {error}\n\n")
            
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        
        # Prepara payload
        payload = {
            "marca": message["marca"],
            "produtos": [{
                "id": p["id"],
                "nome": p["nome"],
                "preco": p["preco"],
                "porcentagem": p["porcentagem"],
                "dataInicio": p["dataInicio"],
                "dataFim": p["dataFim"]
            } for p in message["produtos"]]
        }
        
        print("Enviando para API")        
        response = requests.post(API_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("Mensagem processada com sucesso")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            error_msg = f"Erro {response.status_code} - {response.text[:200]}"
            print(f"{error_msg}")
            
            # Gera log para todos os erros da API
            with open("erros.log", "a", encoding='utf-8') as log:
                log.write(f"[{datetime.now()}] Erro na API\n")
                log.write(f"Tipo: {response.status_code}\n")
                log.write(f"Mensagem Original: {json.dumps(message, indent=2)}\n")
                log.write(f"Resposta da API: {response.text}\n\n")
            
            # Envia para DLQ (incluindo 409)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    except Exception as e:
        error_msg = f"Erro inesperado: {str(e)}"
        print(error_msg)
        
        # Gera log para exceções
        with open("erros.log", "a", encoding='utf-8') as log:
            log.write(f"[{datetime.now()}] Erro Inesperado\n")
            log.write(f"Tipo: {type(e).__name__}\n")
            log.write(f"Detalhes: {str(e)}\n")
            log.write(f"Mensagem Original: {body.decode()}\n\n")
        
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