import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client

load_dotenv(find_dotenv())

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("❌ Faltan SUPABASE_URL o SUPABASE_SERVICE_KEY en .env")

_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
_embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

vectorstore = SupabaseVectorStore(
    client=_supabase,
    embedding=_embeddings,
    table_name="documentos",
    query_name="match_documentos",
)


def buscar_en_base_conocimiento_interno(query: str, top_k: int = 5) -> str:
    try:
        docs = vectorstore.similarity_search(query, k=top_k)
        if not docs:
            return "No encontré información relevante en la base de conocimientos."
        contexto = "Información encontrada:\n\n"
        for i, doc in enumerate(docs, 1):
            contexto += f"[{i}]\n{doc.page_content}\n\n"
        return contexto
    except Exception as e:
        return f"Error al buscar: {str(e)}"


@tool
def buscar_cinebot(consulta: str) -> str:
    """
    Busca información sobre películas en la base de conocimientos de CineBot.
    Usa esta herramienta cuando el usuario pregunte sobre:
    - Sinopsis, trama o de qué trata una película
    - Género, duración, clasificación
    - Reparto, directores, premios
    - Contexto o curiosidades de una película específica

    Args:
        consulta: La pregunta o tema a buscar
    """
    print(f"   🔍 Buscando en KB: '{consulta}'")
    return buscar_en_base_conocimiento_interno(consulta)
