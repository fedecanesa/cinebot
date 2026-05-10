"""
Agente IA Completo: Base de Conocimiento + Internet + Histórico
- Tool 1: Base de Conocimiento (RAG con Pinecone)
- Tool 2: Búsqueda en Internet (Tavily)
- Histórico: Guarda conversaciones en PostgreSQL

Autor: Ing. Kevin Inofuente Colque - DataPath
"""

import os
import sys
import uuid
from datetime import datetime
from urllib.parse import quote_plus
from zoneinfo import ZoneInfo

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Agregar el directorio actual al path para importar tools (portable para despliegue)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_postgres import PostgresChatMessageHistory
import psycopg

# Importar tools desde la carpeta tools/
from tools.Base_de_conocimiento import buscar_cinebot
from tools.Busqueda_internet import buscar_internet
from tools.Hora_y_fecha import obtener_fecha_hora
from tools.Cartelera import consultar_cartelera
from tools.Reserva import crear_reserva, consultar_reserva, cancelar_reserva, current_session_id

# ============================================
# 1. CONFIGURACIÓN DE BASE DE DATOS (Histórico)
# ============================================
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

if not all([DB_USER, DB_PASSWORD, DB_HOST]):
    raise ValueError(
        "❌ Faltan variables de base de datos en .env\n"
        "Requeridas: DB_USER, DB_PASSWORD, DB_HOST"
    )

DATABASE_URL = f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"🔌 Conectando como: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ============================================
# 1.5 FUNCIÓN PARA OBTENER CONEXIÓN CON PREPARED STATEMENTS DESHABILITADOS
# ============================================
def get_db_connection():
    """Obtiene una nueva conexión compatible con poolers tipo PgBouncer."""
    try:
        conn = psycopg.connect(
            DATABASE_URL,
            autocommit=True,
            options="-c statement_timeout=30000",
            prepare_threshold=None,
        )
        return conn
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        return None

# ============================================
# 2. LISTA DE TOOLS DISPONIBLES
# ============================================
tools = [
    consultar_cartelera,  # Cartelera y horarios desde la base de datos
    crear_reserva,        # Reserva de entradas (requiere funcion_id, cantidad, tipo)
    consultar_reserva,    # Consulta reserva por código
    cancelar_reserva,     # Cancela reserva y libera asientos
    buscar_cinebot,       # Información de películas (base de conocimiento Supabase)
    buscar_internet,      # Noticias, críticas y estrenos externos
    obtener_fecha_hora,   # Fecha y hora actual por zona horaria
]

# ============================================
# 3. CONFIGURACIÓN DEL MODELO CON TOOLS
# ============================================
chat = init_chat_model("gpt-4.1", temperature=0.7)
chat_con_tools = chat.bind_tools(tools)

# ============================================
# 4. PROMPT DEL AGENTE + CONTEXTO FECHA/HORA
# ============================================
AGENT_TIMEZONE = os.getenv("AGENT_TIMEZONE", "America/Lima")


def _contexto_fecha_hora() -> str:
    """Fecha y hora actual para inyectar en el system prompt (cada turno)."""
    try:
        tz = ZoneInfo(AGENT_TIMEZONE)
    except Exception:
        tz = ZoneInfo("America/Lima")
    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S") + f" (zona {AGENT_TIMEZONE})"

system_prompt = """
<Rol>
Sos CineBot, un asistente inteligente especializado en películas, cartelera de cine, estrenos y recomendaciones.
Podés mostrar la cartelera actualizada, sugerir el mejor horario y reservar entradas directamente desde la conversación.
</Rol>

<Personalidad>
- Cercano, claro y amigable
- Profesional pero relajado
- Con un toque ligero de humor (sin exagerar)
- Natural, como alguien que sabe de cine y recomienda bien
</Personalidad>

<Inicio_Conversacion>

Si el usuario inicia con un saludo o sin contexto:

Respondé de forma cálida y breve, por ejemplo:
"¡Hola! 🎬 ¿Estás buscando algo para ver hoy o querés que te recomiende algo?"

No seas largo ni invasivo.

</Inicio_Conversacion>

<Herramientas>

Tenés estas herramientas disponibles. Usalas con criterio:

1. consultar_cartelera → para saber qué hay en cartelera, en qué horarios y a qué precios.
   Usala siempre que el usuario pregunte por funciones, horarios o disponibilidad.

2. crear_reserva → para confirmar y guardar una reserva.
   SOLO usarla cuando el usuario haya confirmado explícitamente: funcion_id, cantidad y tipo (general/premium).

3. consultar_reserva → para verificar el estado de una reserva por código.

4. cancelar_reserva → para cancelar una reserva confirmada y liberar los asientos. SOLO usarla cuando el usuario haya confirmado explícitamente que quiere cancelar.

5. buscar_cinebot → para información detallada sobre películas: sinopsis, género, reparto, contexto.

6. buscar_internet → para noticias, críticas, tráilers o estrenos que NO están en cartelera.
   No la uses para horarios o disponibilidad — eso lo maneja consultar_cartelera.

7. obtener_fecha_hora → solo si el usuario pregunta la hora o si necesitás confirmar la fecha actual.

Nunca menciones herramientas, RAG, bases de datos ni el sistema al usuario.

</Herramientas>

<Comportamiento>

1. CARTELERA Y HORARIOS

Cuando el usuario pregunta qué hay para ver o en qué horarios:
- Usá consultar_cartelera para obtener la información real
- Presentá las opciones de forma clara y atractiva, INCLUYENDO siempre la fecha de las funciones
- Si hay varias películas, destacá brevemente por qué cada una puede ser buena opción

---

2. FLUJO DE RESERVA

Cuando el usuario quiere comprar o reservar entradas:

Paso 1 — Consultá la cartelera para mostrar opciones
Paso 2 — Presentá horarios con precios y disponibilidad
Paso 3 — Confirmá con el usuario: película, horario, cantidad y tipo (general/premium)
Paso 4 — Una vez que tenés los cuatro datos confirmados, ANTES de ejecutar la reserva, ofrecé UN combo de comida adecuado al contexto. Usá esta lógica:
   - Hora antes de las 15hs → combo más liviano; desde las 15hs → combo completo
   - 1 entrada → Combo Individual; 2 entradas → Combo Pareja; 3 o más → Combo Familiar
   - Acción/thriller → con Nachos; familiar → mención apta para chicos; drama/romance → sin énfasis en comida pesada
   Menú disponible:
   · Combo Individual: Pochoclos medianos + Gaseosa grande — $2.800
   · Combo Pareja: 2× Pochoclos grandes + 2× Gaseosas — $5.200
   · Familiar: 2× Pochoclos + 4× Gaseosas + Nachos — $8.500
   · Premium: Pochoclos grandes + Gaseosa + Nachos + Chocolate — $3.900
   Mencioná solo el combo más adecuado. Ejemplo: "Antes de confirmar, ¿querés agregar el Combo Pareja (2× Pochoclos + 2× Gaseosas — $5.200)? Lo retirás en el mismo mostrador."
   Si el usuario rechaza o no responde al menú → avanzá igual con la reserva.
Paso 5 — Verificá internamente que el funcion_id corresponde EXACTAMENTE a la película y el horario confirmados. Si tenés alguna duda, volvé a llamar consultar_cartelera. Nunca uses un funcion_id de una película diferente a la solicitada.
Paso 6 — Ejecutá crear_reserva con los datos confirmados
Paso 7 — Compartí el código de reserva e indicá que debe presentarlo en boletería

Si el usuario dice "quiero 2 entradas para las 20hs" sin confirmar el tipo → preguntá: "¿General o Premium?"

---

3. CONSULTA DE RESERVA EXISTENTE

Si el usuario menciona un código tipo "CIN-XXXXX" o pregunta por su reserva → usá consultar_reserva.

---

4. CANCELACIÓN DE RESERVA

Si el usuario quiere cancelar una reserva:

Paso 1 — Usá consultar_reserva para mostrar los datos de la reserva (película, fecha, hora, entradas)
Paso 2 — Pedí confirmación explícita antes de cancelar. Ejemplo: "¿Confirmás que querés cancelar tu reserva de Thunderbolts* el viernes a las 14:00?"
Paso 3 — Solo si el usuario confirma → ejecutá cancelar_reserva
Paso 4 — Confirmá la cancelación y aclará que los asientos fueron liberados

Si la reserva ya está cancelada o usada → informalo sin intentar cancelar de nuevo.

---

5. INFORMACIÓN DE PELÍCULAS

Cuando el usuario consulta por una película específica:
- Usá buscar_cinebot para información de la base de conocimiento
- Explicá de qué trata (SIN SPOILERS), género, duración, tono
- Sumá contexto: para qué mood o momento es ideal

---

6. RECOMENDACIONES PERSONALIZADAS

Tenés acceso al historial completo de esta conversación.
Usalo activamente y de forma natural:
- Si antes mencionó un género favorito → priorizalo en sugerencias
- Si ya reservó una película → reconocelo como contexto ("la última vez fuiste a ver X...")
- Si pidió algo de acción → no le ofrezcas comedia romántica sin razón
No digas "según tu historial" — simplemente usá esa información como lo haría cualquier persona que recuerda la conversación.

---

7. USUARIO POCO CLARO

Si el usuario es muy general:
- Hacé preguntas suaves para entender mejor

Ejemplo:
"¿Te pinta algo más de acción, comedia o algo tranqui?"

---

8. FUERA DE DOMINIO

Si el usuario pregunta algo fuera del cine (recetas, clima, política, etc.):
- Respondé con humor ligero y redirigí

Ejemplo:
"Uh, me agarraste fuera de cartelera 😅 Yo soy más de películas. Pero si querés, te recomiendo algo para ver mientras comés."

---

9. CIERRE DE RESPUESTA

Cuando tenga sentido, cerrá con algo que invite a seguir:
- "¿Querés que te reserve las entradas?"
- "¿Vas solo o en grupo?"
- "¿Buscás algo más específico?"

No lo hagas siempre, solo cuando aporte. Después de confirmar una reserva, no ofrezcas otra película.

</Comportamiento>

<Reglas>

- SOLO responder sobre cine, películas y entretenimiento
- NUNCA inventar información ni horarios
- NO dar spoilers
- NO hablar de herramientas, RAG ni bases de datos
- NO decir "según el sistema" ni "según mis datos"
- Siempre confirmá los datos de reserva antes de ejecutarla
- Si no hay información suficiente → decilo claramente y ofrecé alternativas

</Reglas>

<Formato_Respuesta>

Para cartelera, cuando haya varias funciones:

📅 Funciones para [día DD/MM/YYYY]

🎬 Título
- Género: | Duración: | Clasificación:
- Horarios: [hora] — [sala] | General $X | Premium $X

Para una película individual:

🎬 Título
- Género:
- Duración:
- De qué trata:
- Por qué te puede gustar:

No usar formato rígido para conversación natural.

</Formato_Respuesta>
"""

# ============================================
# 5. CREAR TABLA DE HISTORIAL
# ============================================
def crear_tabla_historial():
    try:
        sync_connection = psycopg.connect(DATABASE_URL)
        PostgresChatMessageHistory.create_tables(sync_connection, "chat_history")
        sync_connection.close()
    except Exception as e:
        print(f"⚠️ Nota sobre tabla: {e}")

crear_tabla_historial()

# ============================================
# 6. HISTÓRICO DE CONVERSACIÓN
# ============================================
def get_session_history(session_id: str) -> PostgresChatMessageHistory:
    """
    Obtiene el historial de una sesión.
    Crea una nueva conexión para cada request para evitar conflictos de prepared statements.
    """
    db_conn = get_db_connection()
    if not db_conn:
        raise RuntimeError("No se pudo conectar a la base de datos")
    
    history = PostgresChatMessageHistory(
        "chat_history",
        session_id,
        sync_connection=db_conn
    )
    return history, db_conn

# ============================================
# 7. FUNCIÓN DE CHAT CON AGENTE + TOOLS
# ============================================
def chat_con_agente(mensaje_usuario: str, session_id: str) -> str:
    """
    Ejecuta el agente con tools y memoria.
    El agente decide si usar herramientas o responder directamente.
    """
    # Obtener historial
    history, db_conn = get_session_history(session_id)
    mensajes_previos = history.messages
    
    # Construir mensajes para el modelo (inyectamos fecha/hora actual en cada turno)
    system_content = (
        system_prompt
        + "\n\n---\nFECHA Y HORA ACTUAL (referencia para este turno): "
        + _contexto_fecha_hora()
    )
    messages = [{"role": "system", "content": system_content}]
    
    # Agregar historial
    for msg in mensajes_previos:
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})
    
    # Agregar mensaje actual
    messages.append({"role": "user", "content": mensaje_usuario})
    
    # Inyectar session_id para que crear_reserva pueda vincularlo a la conversación
    token = current_session_id.set(session_id)

    try:
        # Invocar modelo con tools
        response = chat_con_tools.invoke(messages)

        # Procesar tool calls si existen
        if response.tool_calls:
            # Ejecutar cada tool
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # Buscar y ejecutar la tool
                for t in tools:
                    if t.name == tool_name:
                        result = t.invoke(tool_args)
                        tool_results.append({
                            "tool_call_id": tool_call["id"],
                            "result": result
                        })
                        break

            # Agregar respuesta del modelo con tool calls y resultados
            messages.append(response)
            for tr in tool_results:
                messages.append(ToolMessage(
                    content=tr["result"],
                    tool_call_id=tr["tool_call_id"]
                ))

            # Segunda llamada para obtener respuesta final
            final_response = chat_con_tools.invoke(messages)
            respuesta_final = final_response.content
        else:
            # Sin tool calls, respuesta directa
            respuesta_final = response.content

        # Guardar en historial
        history.add_user_message(mensaje_usuario)
        history.add_ai_message(respuesta_final)

        return respuesta_final
    finally:
        current_session_id.reset(token)
        try:
            db_conn.close()
        except Exception:
            pass


# ============================================
# 8. LOOP DE CONVERSACIÓN
# ============================================
def main():
    print("=" * 60)
    print("🎬 CineBot - Agente COMPLETO (Cartelera + BC + Internet + Memoria)")
    print("=" * 60)
    print("🔧 Tools disponibles:")
    for t in tools:
        print(f"   - {t.name}")
    print("💾 Historial: PostgreSQL")
    
    # Menú de sesión
    print("\nOpciones de sesión:")
    print("  1. Nueva conversación")
    print("  2. Continuar sesión existente (pegar UUID)")
    
    opcion = input("\nElige (1/2): ").strip()
    
    if opcion == "2":
        session_id = input("Pega el UUID de la sesión: ").strip()
        try:
            uuid.UUID(session_id)
        except ValueError:
            print("⚠️ UUID inválido. Creando nueva sesión...")
            session_id = str(uuid.uuid4())
    else:
        session_id = str(uuid.uuid4())
    
    print(f"\n📝 Session ID: {session_id}")
    print("   (Guarda este ID para continuar después)")
    print("✅ El agente puede consultar cartelera, reservar y buscar en internet")
    print("Escribe 'salir' para volver al menú.\n")
    
    while True:
        usuario = input("Tú: ").strip()
        
        if usuario.lower() in ['salir', 'exit', 'quit']:
            print(f"\n💾 Tu sesión está guardada.")
            print(f"   UUID: {session_id}")
            print("👋 ¡Hasta luego!")
            break
        
        if not usuario:
            continue
        
        try:
            respuesta = chat_con_agente(usuario, session_id)
            print(f"\n🎬 CineBot: {respuesta}\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")



if __name__ == "__main__":
    main()
