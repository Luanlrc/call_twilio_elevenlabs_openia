import os
from elevenlabs import ElevenLabs
from elevenlabs.conversational_ai.conversation import ConversationInitiationData, Conversation
from interfaces.audio_interface import TwilioAudioInterface
from utils.logger import log_info, log_error
from config import ELEVENLABS_API_KEY, AGENT_ID

class ElevenLabsService:
    def __init__(self):
        self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    async def create_conversation(self, websocket, stream_sid) -> tuple[Conversation, TwilioAudioInterface]:
        """
        Cria e configura uma nova conversação com o agente ElevenLabs.
        Retorna a conversação e a interface de áudio configurada.
        """
        try:
            # Inicializa a interface de áudio do Twilio
            twilio_interface = TwilioAudioInterface(websocket, stream_sid)
            
            # Configura e inicia a conversação do Elevenlabs
            config = ConversationInitiationData()
            conversation = Conversation(
                client=self.client,
                agent_id=AGENT_ID,
                requires_auth=True,
                audio_interface=twilio_interface,
                config=config,
                callback_agent_response=lambda response: log_info("🤖", f"Agente: {response}"),
                callback_user_transcript=lambda transcript: log_info("👤", f"Usuário: {transcript}"),
                callback_agent_response_correction=lambda original, correction: log_info("📝", f"Correção: {original} -> {correction}")
            )
            
            return conversation, twilio_interface

        except Exception as e:
            log_error("❌", f"Erro ao criar conversação: {e}")
            raise

    @staticmethod
    async def start_conversation(conversation: Conversation, twilio_interface: TwilioAudioInterface):
        """Inicia uma sessão de conversação."""
        try:
            # Inicia a sessão
            conversation.start_session()  # Método síncrono
            twilio_interface.conversation = conversation
            log_info("✅", "Sessão iniciada com sucesso")
            
        except Exception as e:
            log_error("❌", f"Erro ao iniciar sessão: {e}")
            if twilio_interface:
                twilio_interface.stop()
            raise

    @staticmethod
    async def end_conversation(conversation: Conversation, twilio_interface: TwilioAudioInterface):
        """Finaliza uma sessão de conversação de forma segura."""
        try:
            if twilio_interface:
                twilio_interface.stop()
            
            if conversation:
                conversation.end_session()  # Método síncrono
                twilio_interface.wait_for_session_end()  # Método síncrono
                log_info("👋", "Sessão finalizada com sucesso")
                
        except Exception as e:
            log_error("❌", f"Erro ao finalizar sessão: {e}")

    @staticmethod
    async def process_audio_input(twilio_interface: TwilioAudioInterface, audio_payload: str):
        """Processa entrada de áudio do Twilio."""
        try:
            await twilio_interface.process_input(audio_payload)
        except Exception as e:
            log_error("❌", f"Erro ao processar áudio: {e}")
            raise