# Assistente de Voz com Twilio, OpenAI e ElevenLabs

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Sistema de conversação por voz que integra:
- [Twilio Voice](https://www.twilio.com/docs/voice) para chamadas telefônicas
- [OpenAI Realtime API](https://platform.openai.com/docs/) para processamento de linguagem natural
- [ElevenLabs](https://elevenlabs.io/) para síntese de voz de alta qualidade

## 🌟 Funcionalidades

- ☎️ Chamadas telefônicas bidirecionais via Twilio
- 🤖 Processamento de linguagem natural em tempo real com OpenAI
- 🗣️ Síntese de voz natural com ElevenLabs
- ⚡ Streaming de áudio em tempo real
- 🎯 Detecção de interrupção de fala
- 🔄 Conversão automática entre formatos de áudio

## 🚀 Começando

### Pré-requisitos

- Python 3.9+ ([Download](https://www.python.org/downloads/))
- Conta Twilio ([Criar conta](https://www.twilio.com/try-twilio))
- Número Twilio com capacidade de voz ([Instruções](https://help.twilio.com/articles/223135247))
- Conta OpenAI com acesso à API Realtime ([Registro](https://platform.openai.com/))
- Conta ElevenLabs ([Registro](https://elevenlabs.io/))

### 🔧 Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. **Configure o ambiente virtual (recomendado)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   .\venv\Scripts\activate  # Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas chaves de API
   ```

### 📡 Configuração para Desenvolvimento

1. **Inicie o túnel ngrok**
   ```bash
   ngrok http 5050
   ```

2. **Configure o Twilio**
   - Acesse o [Console Twilio](https://console.twilio.com/)
   - Em "Phone Numbers" > "Manage" > "Active Numbers"
   - Configure o webhook para: `https://seu-tunnel.ngrok.app/incoming-call`

3. **Inicie o servidor**
   ```bash
   python main.py
   ```

## 🎯 Uso

1. Ligue para seu número Twilio configurado
2. Aguarde a mensagem de boas-vindas
3. Comece a conversar com o assistente

### Recursos Avançados

#### Configuração da IA Falando Primeiro
```python
# Em streaming_twilio_openia_agent.py
# Descomente para a IA falar primeiro:
await send_initial_conversation_item(openai_ws)
```

#### Ajuste de Interrupção de Fala
O sistema detecta quando o usuário começa a falar e interrompe a IA automaticamente.

## 📚 Documentação

Para informações detalhadas sobre:
- Arquitetura do sistema
- API Reference
- Guias de uso
- Solução de problemas

Consulte nossa [Documentação Completa](DOCUMENTATION.md).

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia nosso [Guia de Contribuição](CONTRIBUTING.md) e [Código de Conduta](CODE_OF_CONDUCT.md).

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ✨ Agradecimentos

- Twilio pela infraestrutura de telefonia
- OpenAI pela API de processamento de linguagem natural
- ElevenLabs pela síntese de voz de alta qualidade

## 👤 Autor

Desenvolvido por Luan Cordeiro

---

⭐️ Se este projeto te ajudou, considere dar uma estrela!
