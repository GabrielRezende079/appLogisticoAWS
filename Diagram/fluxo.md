Fluxo de Processamento — Sistema de Pedidos com Geolocalização
🔁 Visão geral

O sistema foi dividido em 3 funções Lambda escritas em Python, conectadas por 2 filas SQS e 2 tabelas DynamoDB.
Tudo funciona de forma assíncrona — ou seja, cada parte faz sua tarefa e passa a bola pra próxima.

🧩 Estrutura
Cliente (App ou API)
    │
    ▼
[Lambda 1] confirmarPedido
    │
    ▼
[SQS] pedidos-confirmados
    │
    ▼
[Lambda 2] processarGeolocalizacao
    │
    ▼
[SQS] geolocalizacao-processada
    │
    ▼
[Lambda 3] despacharPedido
    │
    ▼
[SNS] notificações

🚀 Etapas detalhadas
🟢 1. confirmarPedido (entrada do sistema)

Gatilho: chamada HTTP via API Gateway (ex: POST /pedidos)

Função: recebe o pedido feito pelo cliente.

O que faz:

Lê o corpo do pedido (pedido_id, cliente_id, produto).

Salva no DynamoDB (Tabela de Pedidos) com status "confirmado".

Envia uma mensagem JSON pra fila pedidos-confirmados.

📤 Saída: mensagem SQS com dados do pedido pronto para processamento de geolocalização.

🟡 2. processarGeolocalizacao (processamento intermediário)

Gatilho: mensagens que chegam na fila pedidos-confirmados.

Função: escolhe o galpão mais próximo do cliente.

O que faz:

Lê os dados do pedido recebidos da fila.

Consulta a Tabela de Galpões no DynamoDB.

Usa a função haversine() pra calcular a distância entre o cliente e cada galpão.

Define o galpão mais próximo (melhor_galpao).

Atualiza o pedido adicionando galpao_destino.

Envia o pedido atualizado pra fila geolocalizacao-processada.

📤 Saída: mensagem SQS com o pedido e o galpão escolhido.

🔵 3. despacharPedido (finalização e notificação)

Gatilho: mensagens da fila geolocalizacao-processada.

Função: despacha o pedido e notifica via SNS.

O que faz:

Lê o pedido vindo da fila.

Atualiza a Tabela de Pedidos com o status "enviado" e o ID do galpão.

Publica uma mensagem no tópico SNS avisando que o pedido foi despachado.

📤 Saída: notificação SNS (pode ser enviada a e-mail, SMS, API, etc.).

🗄️ Recursos envolvidos
Tipo	Nome	Usado por	Descrição
DynamoDB	pedidos	confirmarPedido, despacharPedido	Guarda informações dos pedidos
DynamoDB	galpoes	processarGeolocalizacao	Contém a lista de galpões e suas coordenadas
SQS	pedidos-confirmados	confirmarPedido → processarGeolocalizacao	Fila para pedidos recém-confirmados
SQS	geolocalizacao-processada	processarGeolocalizacao → despacharPedido	Fila para pedidos prontos pra despacho
SNS	notificacoes	despacharPedido	Envia avisos para outros sistemas ou usuários
🧠 Benefícios desse fluxo

✅ Escalabilidade: cada Lambda escala independentemente com base na carga das filas.
✅ Baixo acoplamento: se uma função falhar, as mensagens permanecem na fila até serem processadas.
✅ Custo eficiente: você paga apenas quando o código é executado.
✅ Clareza de responsabilidades: cada Lambda faz só uma parte do trabalho.