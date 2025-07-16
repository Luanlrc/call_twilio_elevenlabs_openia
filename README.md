# Assistente de Voz com Twilio Voice e OpenAI Realtime API (Python)

Esta aplicação demonstra como usar Python, [Twilio Voice](https://www.twilio.com/docs/voice) e [Media Streams](https://www.twilio.com/docs/voice/media-streams), e [OpenAI's Realtime API](https://platform.openai.com/docs/) para fazer uma chamada telefônica e conversar com um Assistente de IA.

A aplicação abre websockets com a OpenAI Realtime API e Twilio, e envia áudio de voz de um para o outro para permitir uma conversa bidirecional.

Esta aplicação usa os seguintes produtos Twilio em conjunto com a API Realtime da OpenAI:
- Voz (e TwiML, Media Streams)
- Números de Telefone

> [!NOTA]
> Chamadas de saída estão além do escopo deste aplicativo.

## Pré-requisitos

Para usar o aplicativo, você precisará de:

- **Python 3.9+** Usamos `3.9.13` para desenvolvimento; baixe [aqui](https://www.python.org/downloads/).
- **Uma conta Twilio.** Você pode se inscrever para um teste gratuito [aqui](https://www.twilio.com/try-twilio).
- **Um número Twilio com capacidades de _Voz_.** [Aqui estão as instruções](https://help.twilio.com/articles/223135247-How-to-Search-for-and-Buy-a-Twilio-Phone-Number-from-Console) para comprar um número de telefone.
- **Uma conta OpenAI e uma Chave de API OpenAI.** Você pode se inscrever [aqui](https://platform.openai.com/).
  - **Acesso à API Realtime da OpenAI.**

## Configuração Local

Existem 4 etapas obrigatórias e 1 etapa opcional para colocar o aplicativo em funcionamento localmente para desenvolvimento e teste:
1. Execute o ngrok ou outra solução de tunelamento para expor seu servidor local à internet para testes. Baixe o ngrok [aqui](https://ngrok.com/).
2. (opcional) Crie e use um ambiente virtual
3. Instale os pacotes
4. Configuração do Twilio
5. Atualize o arquivo .env

### Abra um túnel ngrok
Ao desenvolver e testar localmente, você precisará abrir um túnel para encaminhar solicitações ao seu servidor de desenvolvimento local. Estas instruções usam ngrok.

Abra um Terminal e execute:
```
ngrok http 5050
```
Depois que o túnel for aberto, copie a URL de `Forwarding`. Será algo como: `https://[seu-subdominio-ngrok].ngrok.app`. Você precisará disso ao configurar seu número Twilio.

Observe que o comando `ngrok` acima encaminha para um servidor de desenvolvimento rodando na porta `5050`, que é a porta padrão configurada nesta aplicação.

Lembre-se que cada vez que você executar o comando `ngrok http`, uma nova URL será criada, e você precisará atualizá-la em todos os lugares onde ela é referenciada abaixo.

### (Opcional) Criar e usar um ambiente virtual

Para reduzir a desordem em seu ambiente Python global em sua máquina, você pode criar um ambiente virtual. Na linha de comando, digite:

```
python3 -m venv env
source env/bin/activate
```

### Instalar pacotes necessários

No terminal (com o ambiente virtual, se você configurou) execute:
```
pip install -r requirements.txt
```

### Configuração do Twilio

#### Apontar um Número de Telefone para sua URL ngrok
No [Console Twilio](https://console.twilio.com/), vá para **Phone Numbers** > **Manage** > **Active Numbers** e clique no número de telefone adicional que você comprou para este aplicativo nos **Pré-requisitos**.

Nas configurações do seu Número de Telefone, atualize o primeiro dropdown **A call comes in** para **Webhook**, e cole sua URL de encaminhamento ngrok (referenciada acima), seguida de `/incoming-call`. Por exemplo, `https://[seu-subdominio-ngrok].ngrok.app/incoming-call`. Em seguida, clique em **Save configuration**.

### Atualizar o arquivo .env

Crie um arquivo `/env`, ou copie o arquivo `.env.example` para `.env`:

```
cp .env.example .env
```

No arquivo .env, atualize o `OPENAI_API_KEY` com sua chave de API OpenAI dos **Pré-requisitos**.

## Executar o aplicativo
Uma vez que o ngrok esteja rodando, as dependências estejam instaladas, o Twilio esteja configurado corretamente e o `.env` esteja configurado, execute o servidor de desenvolvimento com o seguinte comando:
```
python main.py
```
## Testar o aplicativo
Com o servidor de desenvolvimento em execução, ligue para o número de telefone que você comprou nos **Pré-requisitos**. Após a introdução, você poderá conversar com o Assistente de IA. Divirta-se!

## Recursos especiais

### Fazer a IA falar primeiro
Para fazer o assistente de voz da IA falar antes do usuário, descomente a linha `# await send_initial_conversation_item(openai_ws)`. A saudação inicial é controlada em `async def send_initial_conversation_item(openai_ws)`.

### Tratamento de interrupção/preempção da IA
Quando o usuário fala e a OpenAI envia `input_audio_buffer.speech_started`, o código limpará o buffer do Twilio Media Streams e enviará `conversation.item.truncate` para a OpenAI.

Dependendo das necessidades da sua aplicação, você pode querer usar o evento [`input_audio_buffer.speech_stopped`](https://platform.openai.com/docs/api-reference/realtime-server-events/input-audio-buffer-speech-stopped), ou uma combinação dos dois.

## Desenvolvido por
Desenvolvido por Luan Cordeiro
