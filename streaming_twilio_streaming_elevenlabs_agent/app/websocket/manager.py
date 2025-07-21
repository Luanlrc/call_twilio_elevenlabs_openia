from fastapi import WebSocket
from websocket.handlers import WebSocketHandler
from utils.logger import log_info, log_error

class WebSocketManager:
    def __init__(self):
        self.handler = WebSocketHandler()

    async def handle_connection(self, websocket: WebSocket):
        """
        Gerencia conexões WebSocket.
        Delega o processamento para o handler.
        """
        try:
            log_info("🔌", "Nova conexão WebSocket estabelecida")
            
            # Delega o processamento para o handler
            await self.handler.handle_connection(websocket)
            
        except Exception as e:
            log_error("💥", f"Erro ao gerenciar conexão WebSocket: {e}")
            try:
                await websocket.close()
            except:
                pass
            raise

    async def cleanup(self):
        """
        Limpa recursos do WebSocket Manager.
        Pode ser usado para limpeza adicional no futuro.
        """
        try:
            # Por enquanto não há recursos específicos do manager para limpar
            # Mas mantemos o método para extensibilidade futura
            pass
        except Exception as e:
            log_error("🧹", f"Erro ao limpar recursos do WebSocket Manager: {e}")