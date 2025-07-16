# Teste para verificar a API do ElevenLabs
try:
    from elevenlabs import generate, stream, set_api_key
    print("✅ Importação com generate, stream, set_api_key funcionou")
except ImportError as e:
    print(f"❌ Erro na importação: {e}")

try:
    from elevenlabs import ElevenLabs
    print("✅ Importação com ElevenLabs funcionou")
except ImportError as e:
    print(f"❌ Erro na importação ElevenLabs: {e}")

try:
    import elevenlabs
    print(f"✅ elevenlabs importado. Versão: {elevenlabs.__version__}")
    print(f"📋 Funções disponíveis: {dir(elevenlabs)}")
except ImportError as e:
    print(f"❌ Erro na importação: {e}")