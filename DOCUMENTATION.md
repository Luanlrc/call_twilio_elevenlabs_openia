# Documentação do Sistema de Integração Twilio + ElevenLabs + OpenAI

## Sumário
1. [Introdução](#introdução)
2. [Arquitetura](#arquitetura)
3. [Configuração](#configuração)
4. [API Reference](#api-reference)
5. [Guias de Uso](#guias-de-uso)
6. [Solução de Problemas](#solução-de-problemas)
7. [Limitações e Considerações](#limitações-e-considerações)

## Introdução

### Visão Geral
Este projeto implementa uma integração entre três serviços principais:
- **Twilio**: Gerenciamento de chamadas telefônicas
- **OpenAI**: Processamento de linguagem natural em tempo real
- **ElevenLabs**: Síntese de voz de alta qualidade

### Funcionalidades Principais
- Recebimento e realização de chamadas via Twilio
- Processamento de áudio bidirecional em tempo real
- Conversação natural com IA usando OpenAI
- Síntese de voz com ElevenLabs
- Interrupção natural da fala

## Arquitetura

### Componentes do Sistema
1. **Servidor FastAPI**
   - Endpoints para Twilio
   - Gerenciamento de WebSockets
   - Processamento de eventos

2. **Interfaces de Áudio**
   - Conversão entre formatos (G711 μ-law ↔ PCM)
   - Streaming bidirecional
   - Controle de buffer

3. **Integrações**
   - Twilio Media Streams
   - OpenAI Realtime API
   - ElevenLabs Voice Synthesis

### Fluxo de Dados
1. Entrada de Áudio (Twilio → Sistema)
2. Processamento de Fala (OpenAI)
3. Geração de Resposta (OpenAI → ElevenLabs)
4. Síntese de Voz (ElevenLabs)
5. Saída de Áudio (Sistema → Twilio)

## Configuração

### Pré-requisitos
- Python 3.9+
- Conta Twilio ativa
- Chave API OpenAI
- Conta ElevenLabs

### Variáveis de Ambiente
```env
ELEVENLABS_API_KEY="sua_chave"
ELEVENLABS_AGENT_ID="id_do_agente"
OPENAI_API_KEY="sua_chave_openai"
TWILIO_ACCOUNT_SID="seu_sid"
TWILIO_AUTH_TOKEN="seu_token"
TWILIO_PHONE_NUMBER="+1234567890"
```

### Configuração dos Serviços

#### Twilio
1. Adquirir número de telefone
2. Configurar webhook (URL do seu servidor)
3. Habilitar Media Streams
4. Configurar TwiML para streaming

#### OpenAI
1. Obter API key
2. Configurar modelo GPT-4
3. Ajustar parâmetros de streaming

#### ElevenLabs
1. Criar agente conversacional
2. Configurar voz e parâmetros
3. Obter API key e Agent ID

## API Reference

### Endpoints

#### POST /incoming-call
Recebe chamadas do Twilio e inicia sessão.

#### WebSocket /media-stream
Gerencia streaming de áudio bidirecional.

### Formatos de Áudio
- **Entrada**: G711 μ-law (8kHz)
- **Processamento**: PCM 16-bit
- **Saída**: G711 μ-law (8kHz)

## Guias de Uso

### Iniciando uma Chamada
```python
# Exemplo de código para iniciar chamada
```

### Configurando Prompts
```python
# Exemplo de configuração de prompts
```

### Ajustes de Performance
- Tamanho do buffer: 20ms
- Taxa de amostragem: 8kHz
- Controle de latência

## Solução de Problemas

### Problemas Comuns e Soluções

#### 1. Conversão de Áudio
- **Problema**: Incompatibilidade de formatos
- **Solução**: Conversão automática via `audioop`

#### 2. Latência
- **Problema**: Atrasos na resposta
- **Solução**: Otimização de buffers e streaming

#### 3. Interrupção de Fala
- **Problema**: Sobreposição de vozes
- **Solução**: Sistema VAD e controle de buffer

## Limitações e Considerações

### Limitações Atuais
1. Latência inicial na primeira resposta
2. Possível eco em algumas condições
3. Dependência de conexão estável

### Boas Práticas
1. Monitorar uso de API
2. Implementar fallbacks
3. Manter logs de erro

### Próximos Passos
1. Melhorar detecção de voz
2. Reduzir latência inicial
3. Implementar métricas
4. Adicionar testes automatizados 