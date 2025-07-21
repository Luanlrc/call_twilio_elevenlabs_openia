from elevenlabs import ElevenLabs
from elevenlabs.conversational_ai.conversation import ConversationInitiationData, Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
import time
import os
from dotenv import load_dotenv

"""
Demonstração de conversação em tempo real usando ElevenLabs AI.

Este script implementa uma conversa interativa com um agente ElevenLabs,
utilizando streaming de áudio bidirecional. O agente é capaz de processar
entrada de voz e responder com fala sintetizada em tempo real.

Funcionalidades:
    - Streaming de áudio bidirecional
    - Processamento de voz em tempo real
    - Callbacks para diferentes eventos da conversa
    - Interface de áudio padrão para entrada/saída

Requisitos:
    - Chave API ElevenLabs configurada no .env
    - ID do agente ElevenLabs configurado no .env
"""

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def on_agent_response(response: str):
    """Callback executado quando o agente envia uma resposta."""
    print(f"\nAgente: {response}")

def on_user_transcript(transcript: str):
    """Callback executado quando a fala do usuário é transcrita."""
    print(f"\nUsuário: {transcript}")

def on_agent_response_correction(original: str, correction: str):
    """Callback executado quando há uma correção na resposta do agente."""
    print(f"\nCorreção: {original} -> {correction}")

def main():
    """Função principal que inicializa e gerencia a conversação."""
    agent_id = ELEVENLABS_AGENT_ID
    config = ConversationInitiationData()
    audio_interface = DefaultAudioInterface()
    
    conversation = Conversation(
        client=client,
        agent_id=agent_id,
        requires_auth=True,
        audio_interface=audio_interface,
        config=config,
        callback_agent_response=on_agent_response,
        callback_user_transcript=on_user_transcript,
        callback_agent_response_correction=on_agent_response_correction
    )
    
    try:
        print("Iniciando conversa... (Pressione Ctrl+C para sair)")
        conversation.start_session()
        
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nEncerrando conversa...")
    finally:
        conversation.end_session()
        conversation.wait_for_session_end()

if __name__ == "__main__":
    main() 