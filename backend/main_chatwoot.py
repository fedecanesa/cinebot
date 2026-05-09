"""
Integración del Agente IA con Chatwoot
Webhook para recibir mensajes y responder automáticamente.

Autor: Ing. Kevin Inofuente Colque - DataPath
"""

import os
import sys
import uuid
import logging
import requests
from typing import Optional, List, Any
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv(find_dotenv())

# Agregar el directorio actual al path (portable para despliegue)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar directamente el agente (sin rutas locales)
from agente_basico_hc_bc_toolexterna_pinecone import chat_con_agente

# ============================================
# MODELOS PYDANTIC PARA VALIDACIÓN
# ============================================
class SenderModel(BaseModel):
    """Modelo para validar sender del webhook."""
    id: Optional[int] = None
    type: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        extra = "allow"


class ConversationModel(BaseModel):
    """Modelo para validar conversation del webhook."""
    id: int
    labels: List[str] = Field(default_factory=list)
    status: Optional[str] = None

    class Config:
        extra = "allow"


class ChatwootWebhookModel(BaseModel):
    """Modelo para validar payload del webhook de Chatwoot."""
    event: str
    message_type: Optional[Any] = None  # Puede ser int (0/1) o string ('incoming'/'outgoing')
    content: Optional[str] = None
    conversation: Optional[ConversationModel] = None
    sender: Optional[SenderModel] = None

    class Config:
        extra = "allow"


print("🤖 Cargando Agente D (Pinecone)...")
print("✅ Agente D cargado correctamente")

# ============================================
# CONFIGURACIÓN DE CHATWOOT
# ============================================
CHATWOOT_BASE_URL = os.getenv("CHATWOOT_BASE_URL")
CHATWOOT_ACCOUNT_ID = os.getenv("CHATWOOT_ACCOUNT_ID")
CHATWOOT_API_TOKEN = os.getenv("CHATWOOT_API_ACCESS_TOKEN")

# Etiqueta que activa el bot (opcional, para handoff)
BOT_LABEL = os.getenv("CHATWOOT_BOT_LABEL", "atiende-ia")
# Etiqueta que desactiva la IA: si el usuario/conversación tiene "ia-off", el agente NO responde
TAG_IA_OFF = "ia-off"

if not all([CHATWOOT_BASE_URL, CHATWOOT_ACCOUNT_ID, CHATWOOT_API_TOKEN]):
    print("⚠️  ADVERTENCIA: Faltan variables de Chatwoot en .env")
    print("   Requeridas: CHATWOOT_BASE_URL, CHATWOOT_ACCOUNT_ID, CHATWOOT_API_ACCESS_TOKEN")
else:
    print(f"✅ Chatwoot configurado: {CHATWOOT_BASE_URL}")

# ============================================
# FUNCIONES DE CHATWOOT
# ============================================
def send_chatwoot_message(conversation_id: int, message: str) -> bool:
    """
    Envía un mensaje de respuesta a una conversación en Chatwoot.

    Args:
        conversation_id: ID de la conversación
        message: Mensaje a enviar

    Returns:
        True si se envió correctamente, False si hubo error
    """
    if not all([CHATWOOT_BASE_URL, CHATWOOT_ACCOUNT_ID, CHATWOOT_API_TOKEN]):
        logger.warning(f"Chatwoot no configurado. No se envía mensaje.")
        return False

    url = f"{CHATWOOT_BASE_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations/{conversation_id}/messages"
    headers = {
        'api_access_token': CHATWOOT_API_TOKEN,
        'Content-Type': 'application/json'
    }
    payload = {
        'content': message,
        'message_type': 'outgoing'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"✅ Mensaje enviado a conversación {conversation_id}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error al enviar mensaje: {e}")
        return False


def update_chatwoot_labels(conversation_id: int, labels: list) -> bool:
    """
    Actualiza las etiquetas de una conversación en Chatwoot.

    Args:
        conversation_id: ID de la conversación
        labels: Lista de etiquetas

    Returns:
        True si se actualizó correctamente
    """
    if not all([CHATWOOT_BASE_URL, CHATWOOT_ACCOUNT_ID, CHATWOOT_API_TOKEN]):
        logger.warning(f"Chatwoot no configurado. No se actualizan etiquetas.")
        return False

    url = f"{CHATWOOT_BASE_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations/{conversation_id}/labels"
    headers = {
        'api_access_token': CHATWOOT_API_TOKEN,
        'Content-Type': 'application/json'
    }
    payload = {'labels': labels}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"✅ Etiquetas actualizadas: {labels}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error al actualizar etiquetas: {e}")
        return False


def conversation_id_to_uuid(conversation_id: int) -> str:
    """
    Convierte un conversation_id de Chatwoot a un UUID válido.
    Esto permite usar el mismo session_id para la misma conversación.
    """
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"chatwoot-{conversation_id}"))


# ============================================
# FUNCIONES DE VALIDACIÓN DEL WEBHOOK
# ============================================
def is_incoming_message(message_type: Optional[Any]) -> bool:
    """
    Verifica si el mensaje es entrante (del usuario, no del bot).
    Chatwoot puede usar:
    - message_type = 0 (incoming, numérico)
    - message_type = 1 (outgoing, numérico)
    - message_type = 'incoming' (string)
    - message_type = 'outgoing' (string)
    """
    if message_type is None:
        return False

    # Comparar con valores posibles
    return message_type in (0, 'incoming')


def extract_webhook_data(raw_data: dict) -> tuple[Optional[ChatwootWebhookModel], Optional[str]]:
    """
    Extrae y valida los datos del webhook.

    Returns:
        (parsed_data, error_message) - Si hay error, parsed_data es None
    """
    try:
        payload = ChatwootWebhookModel(**raw_data)
        return payload, None
    except Exception as e:
        logger.warning(f"Validación de payload fallida: {e}")
        return None, str(e)


def get_conversation_id(data: ChatwootWebhookModel) -> Optional[int]:
    """Extrae conversation_id de forma segura."""
    if data.conversation is None:
        return None
    return data.conversation.id


def get_message_content(data: ChatwootWebhookModel) -> Optional[str]:
    """Extrae content de forma segura."""
    return data.content


def get_labels(data: ChatwootWebhookModel) -> List[str]:
    """Extrae labels de forma segura."""
    if data.conversation is None:
        return []
    return data.conversation.labels


def get_sender_type(data: ChatwootWebhookModel) -> Optional[str]:
    """Extrae sender type de forma segura."""
    if data.sender is None:
        return None
    return data.sender.type


# ============================================
# FASTAPI APP
# ============================================
app = FastAPI(
    title="CineBot - Agente IA con Chatwoot",
    description="Webhook para integrar CineBot con Chatwoot y frontend web",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.post("/")
@app.post("/webhook")
async def chatwoot_webhook(request: Request):
    """
    Endpoint que recibe los webhooks de Chatwoot.
    Procesa mensajes entrantes (message_type == 0 o 'incoming') y responde usando el Agente D.

    Ignora:
    - Eventos que no sean 'message_created'
    - Mensajes outgoing (evitar loops)
    - Conversaciones con tag 'ia-off'
    - Payloads sin content o conversation_id
    """
    logger.info(f"📩 REQUEST RECIBIDA EN {request.url.path}")

    try:
        raw_data = await request.json()
    except Exception as e:
        logger.error(f"Error al parsear JSON del webhook: {e}")
        return {"status": "error", "reason": "Invalid JSON"}

    # Log estructura básica
    logger.info(f"Webhook recibido - event: {raw_data.get('event')}, message_type: {raw_data.get('message_type')}")

    # Validar y parsear payload
    data, validation_error = extract_webhook_data(raw_data)
    if data is None:
        logger.warning(f"Payload inválido: {validation_error}")
        return {"status": "error", "reason": "Invalid payload"}

    # ========== FILTRO 1: Verificar que sea 'message_created' ==========
    if data.event != 'message_created':
        logger.info(f"Ignorado: evento no es 'message_created' (es: {data.event})")
        return {"status": "ignored", "reason": "Not a message_created event"}

    # ========== FILTRO 2: Verificar que sea mensaje entrante ==========
    logger.info(f"message_type value: {data.message_type} (type: {type(data.message_type).__name__})")
    if not is_incoming_message(data.message_type):
        logger.info(f"Ignorado: no es mensaje entrante (message_type: {data.message_type})")
        return {"status": "ignored", "reason": "Not an incoming message (outgoing or unknown type)"}

    # ========== EXTRACCIÓN SEGURA DE DATOS ==========
    conversation_id = get_conversation_id(data)
    message_content = get_message_content(data)
    labels = get_labels(data)
    sender_type = get_sender_type(data)

    logger.info(f"Conversación ID: {conversation_id}, sender_type: {sender_type}, labels: {labels}")

    # ========== FILTRO 3: Verificar sender None ==========
    if data.sender is None:
        logger.info(f"Mensaje sin sender (sender=null). Ignorando para evitar loops.")
        return {"status": "ignored", "reason": "Sender is null (outgoing message)"}

    # ========== FILTRO 4: Verificar contenido y conversation_id ==========
    if not message_content or not conversation_id:
        logger.warning(f"Falta content o conversation_id - content: {bool(message_content)}, conv_id: {conversation_id}")
        return {"status": "ignored", "reason": "Missing content or conversation_id"}

    # ========== FILTRO 5: Verificar tag 'ia-off' ==========
    if TAG_IA_OFF in labels:
        logger.info(f"Ignorado: conversación tiene tag '{TAG_IA_OFF}' (IA desactivada)")
        return {"status": "ignored", "reason": f"User has tag '{TAG_IA_OFF}'"}

    logger.info(f"✅ Mensaje válido para procesar: {message_content[:80]}...")

    # ========== DETECCIÓN DE HANDOFF A HUMANO ==========
    human_keywords = ['humano', 'persona', 'asesor', 'agente', 'representante', 'hablar con alguien']
    if any(keyword in message_content.lower() for keyword in human_keywords):
        logger.info(f"🗣️ Transferencia a humano detectada")

        new_labels = [l for l in labels if l != BOT_LABEL]
        new_labels.append('atiende-humano')
        update_chatwoot_labels(conversation_id, new_labels)

        handoff_message = "Entendido. Un asesor humano se pondrá en contacto contigo en breve. ¡Gracias por tu paciencia!"
        send_chatwoot_message(conversation_id, handoff_message)

        return {"status": "success", "action": "human_handoff"}

    # ========== PROCESAR CON EL AGENTE D ==========
    try:
        logger.info(f"🤖 Procesando mensaje con Agente D...")

        session_id = conversation_id_to_uuid(conversation_id)
        logger.info(f"Session ID generada: {session_id[:8]}...")

        respuesta = chat_con_agente(message_content, session_id)

        logger.info(f"✅ Respuesta generada ({len(respuesta)} caracteres)")

        send_chatwoot_message(conversation_id, respuesta)

        return {"status": "success", "action": "agent_response"}

    except Exception as e:
        logger.error(f"❌ Error al procesar mensaje: {e}", exc_info=True)

        error_message = "Disculpa, tuve un problema al procesar tu consulta. Un asesor te atenderá pronto."
        send_chatwoot_message(conversation_id, error_message)

        return {"status": "error", "message": str(e)}


@app.get("/")
def read_root():
    """Endpoint raíz con información del servicio."""
    return {
        "service": "DataBot - Agente IA",
        "version": "2.1.0",
        "agent": "Agente D (RAG + Internet + Memoria)",
        "model": "GPT-4.1",
        "tools": ["buscar_cinebot", "buscar_internet", "obtener_fecha_hora"],
        "chatwoot_configured": all([CHATWOOT_BASE_URL, CHATWOOT_ACCOUNT_ID, CHATWOOT_API_TOKEN]),
        "bot_label": BOT_LABEL,
        "status": "ready"
    }


@app.get("/health")
def health_check():
    """Endpoint de salud del servicio."""
    return {
        "status": "healthy",
        "agent": "Agente D",
        "chatwoot": "connected" if all([CHATWOOT_BASE_URL, CHATWOOT_ACCOUNT_ID, CHATWOOT_API_TOKEN]) else "not configured"
    }


@app.post("/test")
async def test_agent(request: Request):
    """
    Endpoint de prueba para testear el agente sin Chatwoot.

    Body: {"message": "tu pregunta", "session_id": "opcional"}
    """
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Error al parsear JSON en /test: {e}")
        return {"error": "Invalid JSON"}

    message = data.get('message', '')
    session_id = data.get('session_id', str(uuid.uuid4()))

    if not message:
        return {"error": "Debes proporcionar un 'message' en el body"}

    logger.info(f"🧪 TEST - Mensaje: {message}")
    logger.info(f"Session: {session_id[:8]}...")

    try:
        respuesta = chat_con_agente(message, session_id)
        logger.info(f"✅ Respuesta generada ({len(respuesta)} caracteres)")

        return {
            "message": message,
            "session_id": session_id,
            "response": respuesta,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"❌ Error en /test: {e}", exc_info=True)
        return {
            "message": message,
            "error": str(e),
            "status": "error"
        }


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


@app.post("/chat")
async def chat_endpoint(body: ChatRequest):
    """
    Endpoint principal para el frontend web.
    Mantiene sesión conversacional por session_id.

    Body: {"message": "texto", "session_id": "uuid-opcional"}
    Response: {"response": "texto", "session_id": "uuid"}
    """
    session_id = body.session_id or str(uuid.uuid4())

    logger.info(f"💬 CHAT — session={session_id[:8]}... mensaje={body.message[:60]}")

    try:
        respuesta = chat_con_agente(body.message, session_id)
        return {"response": respuesta, "session_id": session_id}
    except Exception as e:
        logger.error(f"❌ Error en /chat: {e}", exc_info=True)
        return {"response": "Hubo un problema procesando tu mensaje. Intentalo de nuevo.", "session_id": session_id}


# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    print()
    print("=" * 60)
    print("🚀 INICIANDO DATABOT CON CHATWOOT")
    print("=" * 60)
    print(f"🤖 Agente: D (RAG + Internet + Memoria)")
    print(f"🧠 Modelo: GPT-4.1")
    print(f"🔧 Tools: buscar_cinebot, buscar_internet, obtener_fecha_hora")
    print(f"💾 Historial: PostgreSQL")
    print(f"🏷️  Etiqueta bot (handoff): {BOT_LABEL or 'ninguna'}")
    print(f"🚫 No responde si tiene tag: {TAG_IA_OFF}")
    print("=" * 60)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
