"""
Tool: Cartelera de cine
Consulta funciones disponibles directamente desde la base de datos.
"""

import os
from collections import defaultdict
from datetime import date
from urllib.parse import quote_plus

import psycopg
from dotenv import find_dotenv, load_dotenv
from langchain_core.tools import tool

load_dotenv(find_dotenv())


def _get_conn():
    user = os.getenv("DB_USER")
    password = quote_plus(os.getenv("DB_PASSWORD", ""))
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "postgres")
    return psycopg.connect(f"postgresql://{user}:{password}@{host}:{port}/{name}")


@tool
def consultar_cartelera(pelicula: str = "", fecha: str = "", genero: str = "") -> str:
    """
    Consulta las funciones disponibles en cartelera.

    Usá esta herramienta cuando el usuario quiera saber:
    - Qué películas hay para ver hoy o en una fecha específica
    - En qué horarios da una película determinada
    - Qué hay de un género en particular (acción, comedia, terror, etc.)

    El resultado incluye el ID de función (funcion_id) necesario para crear una reserva.

    Args:
        pelicula: Nombre o parte del nombre de la película (vacío = todas)
        fecha: Fecha en formato YYYY-MM-DD (vacío = hoy)
        genero: Género de la película (vacío = todos)
    """
    print(f"   🎬 Consultando cartelera — pelicula='{pelicula}' fecha='{fecha}' genero='{genero}'")

    try:
        fecha_consulta = date.fromisoformat(fecha) if fecha else date.today()
    except ValueError:
        fecha_consulta = date.today()

    query = """
        SELECT
            p.titulo,
            p.genero,
            p.duracion_min,
            p.clasificacion,
            f.id AS funcion_id,
            f.hora,
            s.nombre AS sala,
            f.asientos_general_disponibles,
            f.asientos_premium_disponibles,
            f.precio_general,
            f.precio_premium
        FROM funciones f
        JOIN peliculas p ON f.pelicula_id = p.id
        JOIN salas s ON f.sala_id = s.id
        WHERE f.fecha = %s
          AND p.activa = TRUE
          AND (f.asientos_general_disponibles > 0 OR f.asientos_premium_disponibles > 0)
    """
    params: list = [fecha_consulta]

    if pelicula.strip():
        query += " AND LOWER(unaccent(p.titulo)) LIKE LOWER(unaccent(%s))"
        params.append(f"%{pelicula}%")

    if genero.strip():
        query += " AND LOWER(p.genero) LIKE %s"
        params.append(f"%{genero.lower()}%")

    query += " ORDER BY p.titulo, f.hora"

    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
    except Exception as e:
        # unaccent extension may not exist; retry without it
        if "unaccent" in str(e):
            query = query.replace(
                "LOWER(unaccent(p.titulo)) LIKE LOWER(unaccent(%s))",
                "LOWER(p.titulo) LIKE LOWER(%s)",
            )
            try:
                with _get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute(query, params)
                        rows = cur.fetchall()
            except Exception as e2:
                return f"Error al consultar cartelera: {e2}"
        else:
            return f"Error al consultar cartelera: {e}"

    if not rows:
        return (
            f"No hay funciones disponibles para el {fecha_consulta.strftime('%d/%m/%Y')}"
            + (f" con película '{pelicula}'" if pelicula else "")
            + (f" de género '{genero}'" if genero else "")
            + "."
        )

    peliculas: dict = defaultdict(list)
    meta: dict = {}

    for row in rows:
        titulo, genero_p, duracion, clasificacion, funcion_id, hora, sala, gen_disp, prem_disp, precio_gen, precio_prem = row
        if titulo not in meta:
            meta[titulo] = (genero_p, duracion, clasificacion)
        peliculas[titulo].append((funcion_id, hora, sala, gen_disp, prem_disp, precio_gen, precio_prem))

    resultado = f"CARTELERA — {fecha_consulta.strftime('%d/%m/%Y')}\n\n"
    for titulo, funciones in peliculas.items():
        genero_p, duracion, clasificacion = meta[titulo]
        resultado += f"🎬 {titulo.upper()}\n"
        resultado += f"   {genero_p} | {duracion} min | {clasificacion}\n"
        for funcion_id, hora, sala, gen_disp, prem_disp, precio_gen, precio_prem in funciones:
            hora_str = hora.strftime("%H:%M") if hasattr(hora, "strftime") else str(hora)[:5]
            resultado += f"   • [ID:{funcion_id}] {hora_str} — {sala}"
            if gen_disp and gen_disp > 0:
                resultado += f" | General ${precio_gen:.0f} ({gen_disp} disp.)"
            if prem_disp and prem_disp > 0:
                resultado += f" | Premium ${precio_prem:.0f} ({prem_disp} disp.)"
            resultado += "\n"
        resultado += "\n"

    return resultado.strip()
