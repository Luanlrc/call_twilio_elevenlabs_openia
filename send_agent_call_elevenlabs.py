from elevenlabs import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv()

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

phone = "+999999999999"
agent_id=os.getenv("ELEVENLABS_AGENT_ID")

client.conversational_ai.twilio.outbound_call(
    agent_id=agent_id,
    agent_phone_number_id=os.getenv("ELEVENLABS_AGENT_PHONE_NUMBER_ID"),
    to_number = phone
)