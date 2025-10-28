import json
import boto3
import math
import os

sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

QUEUE_URL = os.environ['QUEUE_GEOLOCALIZACAO_PROCESSADA']
TABELA_GALPOES = os.environ['TABELA_GALPOES']

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def lambda_handler(event, context):
    for record in event['Records']:
        pedido = json.loads(record['body'])
        cliente = {'lat': -23.5, 'lon': -46.6}  # Exemplo (São Paulo)
        
        tabela = dynamodb.Table(TABELA_GALPOES)
        galpoes = tabela.scan()['Items']
        
        melhor_galpao = min(galpoes, key=lambda g: haversine(cliente['lat'], cliente['lon'], g['lat'], g['lon']))
        
        pedido['galpao_destino'] = melhor_galpao['id']
        
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(pedido)
        )

    return {'statusCode': 200}
