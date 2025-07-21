from elevenlabs import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv()

"""
Script para iniciar chamadas telefônicas automatizadas usando ElevenLabs e Twilio.

Este script permite realizar chamadas de saída (outbound) utilizando um agente virtual
da ElevenLabs. O agente é capaz de manter uma conversa natural usando voz sintetizada
de alta qualidade.

Requisitos:
    - Chave API ElevenLabs configurada
    - ID do agente ElevenLabs configurado
    - ID do número de telefone ElevenLabs configurado
    - Número de telefone de destino válido
"""

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

phone = "+5541995659361"
agent_id=os.getenv("ELEVENLABS_AGENT_ID")

client.conversational_ai.twilio.outbound_call(
    agent_id=agent_id,
    agent_phone_number_id=os.getenv("ELEVENLABS_AGENT_PHONE_NUMBER_ID"),
    to_number = phone
)