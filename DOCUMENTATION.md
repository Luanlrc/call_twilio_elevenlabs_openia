# Integração Twilio + ElevenLabs Agent

Este projeto implementa uma integração entre o Twilio (para chamadas telefônicas) e o ElevenLabs Agent (para conversação por voz). 

## Visão Geral

O sistema permite:
- Receber/fazer chamadas usando Twilio
- Processar áudio bidirecional em tempo real
- Conversar com um agente ElevenLabs
- Interrupção natural da fala quando o usuário começa a falar

## Principais Componentes

1. **TwilioAudioInterface**: 
   - Implementa a interface de áudio para o ElevenLabs
   - Gerencia a conversão de áudio entre os formatos
   - Controla o fluxo de áudio bidirecional

2. **FastAPI Server**:
   - Gerencia endpoints para Twilio
   - Manipula WebSockets para streaming de áudio
   - Processa eventos da chamada

## Problemas Encontrados e Soluções

### 1. Conversão de Áudio

**Problema**: O Twilio usa G711 μ-law enquanto o ElevenLabs usa formatos diferentes.

**Solução**: 
- Implementamos conversão bidirecional entre formatos
- Usamos `audioop` para conversão PCM ↔ μ-law
- Ajustamos taxas de amostragem para compatibilidade

```python
def convert_elevenlabs_to_ulaw(audio_data):
    audio = AudioSegment(
        data=audio_data,
        sample_width=2,
        frame_rate=16000,  # Taxa intermediária controla a velocidade da voz
        channels=1
    )
    audio = audio.set_frame_rate(8000)  # Taxa do Twilio
```

### 2. Velocidade da Voz

**Problema**: A voz do agente estava muito lenta/rápida devido a diferenças nas taxas de amostragem.

**Solução**:
- Ajustamos a taxa de amostragem para 16kHz na entrada
- Convertemos para 8kHz para Twilio
- Adicionamos controle de velocidade via `frame_rate`

### 3. Streaming de Áudio

**Problema**: Envio de áudio em blocos grandes causava latência.

**Solução**:
- Implementamos streaming em chunks de 20ms
- Adicionamos pequenas pausas entre chunks
- Melhoramos a fluidez da conversa

```python
chunk_size = int(8000 * 2 * self._chunk_duration / 1000)
chunks = [audio_payload[i:i+chunk_size] for i in range(0, len(audio_payload), chunk_size)]
```

### 4. Interrupção de Fala

**Problema**: Necessidade de interromper o agente quando o usuário começa a falar.

**Solução**:
- Implementamos detecção de voz (VAD)
- Sistema de interrupção com limpeza de buffer
- Controle de estado de fala

```python
async def handle_speech_started(self):
    if self.agent_is_speaking:
        self.interrupt()
        await self._send_clear_event()
```

## Configuração

### Variáveis de Ambiente (.env)
```
ELEVENLABS_API_KEY="sua_chave"
AGENT_ID="id_do_agente"
TWILIO_ACCOUNT_SID="seu_sid"
TWILIO_AUTH_TOKEN="seu_token"
TWILIO_PHONE_NUMBER="+1234567890"
```

### Twilio
1. Comprar número de telefone
2. Configurar webhook para seu servidor
3. Habilitar Media Streams

### ElevenLabs
1. Criar agente conversacional
2. Configurar prompt do agente
3. Obter API Key e Agent ID

## Ajustes Finos

### Velocidade da Voz
- Controlada por `frame_rate` na conversão de áudio
- 16kHz = velocidade padrão
- Ajustável conforme necessidade

### Qualidade do Áudio
- Formato: PCM 16-bit
- Taxa de amostragem: 8kHz (Twilio)
- Chunks de 20ms para streaming

## Limitações Conhecidas

1. Latência inicial na primeira resposta
2. Possível eco em algumas condições
3. Dependência de conexão estável

## Próximos Passos

1. Melhorar detecção de voz
2. Reduzir latência inicial
3. Implementar fallback para conexões instáveis
4. Adicionar métricas e monitoramento 