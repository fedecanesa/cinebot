"""
Tool: Búsqueda en Internet para CineBot (Tavily)
Permite buscar información actualizada sobre cine, películas, estrenos o noticias del sector.

Proyecto: CineBot
"""

import os
from dotenv import load_dotenv, find_dotenv
from langchain_core.tools import tool

load_dotenv(find_dotenv())

# ============================================
# CONFIGURACIÓN DE TAVILY
# ============================================
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError(
        "❌ Falta TAVILY_API_KEY en .env\n"
        "Obtén tu API key en Tavily."
    )

try:
    from langchain_tavily import TavilySearch
    tavily_search = TavilySearch(max_results=5)
except ImportError:
    from langchain_community.tools.tavily_search import TavilySearchResults
    tavily_search = TavilySearchResults(max_results=5)


@tool
def buscar_internet(consulta: str) -> str:
    """
    Busca información actualizada en internet sobre cine.

    Usa esta herramienta solo cuando el usuario pregunte por:
    - noticias recientes del mundo del cine
    - fechas reales o actualizadas de estreno
    - información que no esté en la base de conocimiento de CineBot

    NO la uses para:
    - preguntas que ya puedan responderse con la base de conocimiento de CineBot
    - saludos o conversación general
    - temas no relacionados con el cine
    

    Args:
        consulta: La pregunta o tema a buscar en internet
    """
    print(f"   🌐 Buscando en internet sobre cine: '{consulta}'")

    try:
        resultados = tavily_search.invoke(consulta)

        if not resultados:
            return "No encontré información relevante en internet."

        respuesta = "Información encontrada en internet:\n\n"

        if isinstance(resultados, list):
            for i, resultado in enumerate(resultados, 1):
                if isinstance(resultado, dict):
                    titulo = resultado.get("title", "Sin título")
                    contenido = resultado.get("content", "")
                    url = resultado.get("url", "")
                else:
                    titulo = f"Resultado {i}"
                    contenido = str(resultado)
                    url = ""

                respuesta += f"[{i}] {titulo}\n"
                respuesta += f"{contenido[:500]}...\n" if len(contenido) > 500 else f"{contenido}\n"
                if url:
                    respuesta += f"Fuente: {url}\n"
                respuesta += "\n"
        else:
            respuesta += str(resultados)

        return respuesta.strip()

    except Exception as e:
        return f"Error al buscar en internet: {str(e)}"


# Alias retrocompatible para código que todavía use el nombre anterior
buscar_internet_cine = buscar_internet