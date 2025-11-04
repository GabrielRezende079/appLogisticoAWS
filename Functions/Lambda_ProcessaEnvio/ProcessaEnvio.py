import json
import boto3
import os

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

TABELA_PEDIDOS = os.environ['TABELA_PEDIDOS']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    for record in event['Records']:
        pedido = json.loads(record['body'])
        pedido_id = pedido['pedido_id']
        galpao = pedido['galpao_destino']

        tabela = dynamodb.Table(TABELA_PEDIDOS)
        tabela.update_item(
            Key={'pedido_id': pedido_id},
            UpdateExpression='SET status = :s, galpao = :g',
            ExpressionAttributeValues={':s': 'enviado', ':g': galpao}
        )

        # Envia notificação (cliente e vendedor)
        mensagem = f"Pedido {pedido_id} foi despachado a partir do galpão {galpao}."
        sns.publish(TopicArn=SNS_TOPIC_ARN, Message=mensagem)

    return {'statusCode': 200}
