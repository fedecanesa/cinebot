# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CineBot** is a FastAPI-based AI agent for the cinema domain, integrated with Chatwoot (customer messaging platform). It uses LangChain with OpenAI's GPT-4.1 model to answer questions about movies, showtimes, releases, and recommendations.

**Key Technologies:**
- FastAPI + Uvicorn (web server)
- LangChain 1.0+ (agent framework)
- OpenAI GPT-4.1 with `text-embedding-ada-002` for embeddings
- Pinecone (vector database for RAG)
- PostgreSQL (conversation history via `langchain-postgres`)
- Chatwoot (customer messaging integration)
- Tavily (web search)

## Architecture

### Request Flow

1. **Chatwoot Webhook** → `main_chatwoot.py`: POST `/webhook` (or POST `/`)
2. **Validation filters** (sequential, fail-fast):
   - Event must be `message_created`
   - `message_type` must be `0` or `'incoming'` (Chatwoot sends both int and string variants)
   - `sender` must not be null (null sender = outgoing message loop prevention)
   - `content` and `conversation_id` must be present
   - Conversation must not have `ia-off` label
3. **Hand-off Detection** → keywords like `humano`, `persona`, `asesor` update label to `atiende-humano` and send a fixed reply
4. **Agent Processing** → `agente_basico_hc_bc_toolexterna_pinecone.chat_con_agente()`
5. **Tool Use** (single-pass, not a loop):
   - Model is called once; if it returns `tool_calls`, all tools are executed
   - Results are appended and the model is called a second time for the final response
   - Tools: `buscar_cinebot` (Pinecone RAG), `buscar_internet` (Tavily), `obtener_fecha_hora`
6. **History** → saved to PostgreSQL via `PostgresChatMessageHistory` (table: `chat_history`)
7. **Response** → `send_chatwoot_message()` posts back to Chatwoot

### Key Components

**Agent** (`agente_basico_hc_bc_toolexterna_pinecone.py`)
- `chat_con_agente(mensaje_usuario, session_id)` — main entry point used by the web server
- `_contexto_fecha_hora()` — injects live timestamp into system prompt each turn
- `get_session_history(session_id)` — opens a new psycopg connection per call (not pooled)
- `main()` — interactive CLI loop for local testing without FastAPI

**Chatwoot Integration** (`main_chatwoot.py`)
- Both `POST /` and `POST /webhook` handle the same webhook logic
- `conversation_id_to_uuid()` — deterministic UUID5 from integer conversation ID
- `is_incoming_message()` — handles Chatwoot's int (`0`) and string (`'incoming'`) variants

**Tools** (`tools/`)
- `Base_de_conocimiento.py` — `buscar_cinebot`: Pinecone similarity search, top-k=5. **Note:** the tool's docstring still says "DATAPATH" (copy from original template) but it searches CineBot's movie knowledge base. Update the docstring when modifying.
- `Busqueda_internet.py` — `buscar_internet`: Tavily search, max 5 results. Falls back from `langchain_tavily` to `langchain_community` on ImportError. Also exports `buscar_internet_cine` alias for backward compatibility.
- `Hora_y_fecha.py` — `obtener_fecha_hora`: stdlib `zoneinfo`, no external API

## Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL running
- API keys: `OPENAI_API_KEY`, `PINECONE_API_KEY`, `TAVILY_API_KEY`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`
- Pinecone index must exist and use `text-embedding-ada-002` embeddings (1536 dims)

### Installation

```bash
pip install -r requirements.txt
```

Note: `supabase` is listed in `requirements.txt` as a legacy dependency — it is not used by any current code.

### Environment Variables (.env)

```bash
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=cinebot-index
DB_USER=postgres
DB_PASSWORD=...
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
TAVILY_API_KEY=...
CHATWOOT_BASE_URL=https://chatwoot.example.com
CHATWOOT_ACCOUNT_ID=1
CHATWOOT_API_ACCESS_TOKEN=...
CHATWOOT_BOT_LABEL=atiende-ia
AGENT_TIMEZONE=America/Lima
```

## Running

### Web Server (Chatwoot integration)

```bash
uvicorn main_chatwoot:app --reload --host 0.0.0.0 --port 8000
```

### Standalone CLI (no Chatwoot required)

```bash
python agente_basico_hc_bc_toolexterna_pinecone.py
```

Prompts for a session ID (new or existing UUID) and enters an interactive loop.

### Test Endpoint (agent without Chatwoot)

```bash
curl -X POST http://localhost:8000/test \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Qué películas hay en cartelera?", "session_id": "optional-uuid"}'
```

### Docker

```bash
docker buildx build --platform linux/amd64 -t fedecanesa/cinebot-backend:latest --push .
docker run -p 8000:8000 --env-file .env fedecanesa/cinebot-backend:latest
```

## Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/webhook` or `/` | POST | Chatwoot webhook |
| `/` | GET | Service info |
| `/health` | GET | Liveness check |
| `/test` | POST | Direct agent test |

## Common Workflows

### Adding a New Tool

1. Create `tools/My_Tool.py` with a `@tool` function
2. Import and add to `tools = [...]` in `agente_basico_hc_bc_toolexterna_pinecone.py`
3. Update system prompt if needed (line ~83)
4. Test via CLI or `/test` endpoint

### Updating the System Prompt

Edit the `system_prompt` string starting at line ~83 in `agente_basico_hc_bc_toolexterna_pinecone.py`. Controls role, personality, behavior rules, and response format.

### Changing Chatwoot Behavior

- **Hand-off keywords:** `human_keywords` list at `main_chatwoot.py:304`
- **Disable AI for a conversation:** add `ia-off` label in Chatwoot UI
- **Bot label for analytics:** set `CHATWOOT_BOT_LABEL` in `.env`

### Managing Conversation History

PostgreSQL table `chat_history` stores messages per UUID session. To clear a session:

```sql
DELETE FROM message_store WHERE session_id = '...';
```

Tables are auto-created on startup via `PostgresChatMessageHistory.create_tables()`.

## Key Design Decisions

**Single-pass tool use** — The agent resolves tool calls in one batch (all tools called in parallel if needed), then makes one final LLM call. There is no multi-step loop where tool results can trigger further tool calls.

**Session ID Conversion** — `conversation_id_to_uuid()` uses UUID5 (deterministic) so the same Chatwoot conversation always maps to the same PostgreSQL session, surviving restarts.

**New DB connection per request** — `get_session_history()` opens a new `psycopg.connect()` each call. For high traffic, consider adding a connection pool.

**Webhook dual-route** — Both `POST /` and `POST /webhook` are registered to the same handler, allowing Chatwoot to be configured with either path.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Faltan variables de Chatwoot" | Chatwoot not configured; agent still works, use `/test` or CLI |
| PostgreSQL connection error | Check `DB_*` env vars, ensure PostgreSQL is running |
| Pinecone index not found | Verify `PINECONE_INDEX_NAME` matches an existing index using `text-embedding-ada-002` |
| Tool returns empty | Check API keys (Tavily, OpenAI), network connectivity, and Pinecone index state |
| Messages loop back | Check `sender` null filter and `message_type` values in logs |
