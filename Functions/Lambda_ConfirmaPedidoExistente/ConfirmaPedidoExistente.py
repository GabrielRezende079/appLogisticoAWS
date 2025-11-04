import json
import boto3
import os
from datetime import datetime

sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

QUEUE_URL = os.environ['QUEUE_PEDIDOS_CONFIRMADOS']
TABELA_PEDIDOS = os.environ['TABELA_PEDIDOS']

def lambda_handler(event, context):
    # Dados do pedido vindos da API Gateway
    body = json.loads(event['body'])
    pedido_id = body['pedido_id']
    cliente_id = body['cliente_id']
    produto = body['produto']

    tabela = dynamodb.Table(TABELA_PEDIDOS)
    tabela.put_item(
        Item={
            'pedido_id': pedido_id,
            'cliente_id': cliente_id,
            'produto': produto,
            'status': 'confirmado',
            'data': datetime.utcnow().isoformat()
        }
    )

    # Envia mensagem para a fila SQS
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps({
            'pedido_id': pedido_id,
            'cliente_id': cliente_id,
            'produto': produto
        })
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'mensagem': 'Pedido confirmado e enviado para processamento'})
    }
