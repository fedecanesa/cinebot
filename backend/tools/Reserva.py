"""
Tool: Reserva de entradas
Crea y consulta reservas directamente en la base de datos.
"""

import os
import random
import string
from contextvars import ContextVar
from urllib.parse import quote_plus

import psycopg
from dotenv import find_dotenv, load_dotenv
from langchain_core.tools import tool

load_dotenv(find_dotenv())

# Inyectado por chat_con_agente() antes de cada llamada al modelo
current_session_id: ContextVar[str] = ContextVar("current_session_id", default="unknown")


def _get_conn():
    user = os.getenv("DB_USER")
    password = quote_plus(os.getenv("DB_PASSWORD", ""))
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "postgres")
    return psycopg.connect(f"postgresql://{user}:{password}@{host}:{port}/{name}")


def _generar_codigo() -> str:
    chars = string.ascii_uppercase + string.digits
    return "CIN-" + "".join(random.choices(chars, k=6))


@tool
def crear_reserva(funcion_id: int, cantidad: int, tipo_entrada: str) -> str:
    """
    Crea una reserva de entradas para una función.

    IMPORTANTE: Usá esta herramienta SOLO cuando el usuario haya confirmado explícitamente:
    - La función (funcion_id del resultado de consultar_cartelera)
    - La cantidad de entradas
    - El tipo: 'general' o 'premium'

    No ejecutes la reserva sin estos tres datos confirmados por el usuario.

    Args:
        funcion_id: ID de la función (obtenido de consultar_cartelera)
        cantidad: Número de entradas (entre 1 y 10)
        tipo_entrada: 'general' o 'premium'
    """
    print(f"   🎟️  Creando reserva — funcion_id={funcion_id}, cantidad={cantidad}, tipo={tipo_entrada}")

    tipo = tipo_entrada.lower().strip()
    if tipo not in ("general", "premium"):
        return "Tipo de entrada inválido. Debe ser 'general' o 'premium'."
    if not (1 <= cantidad <= 10):
        return "La cantidad debe estar entre 1 y 10 entradas."

    campo_asientos = "asientos_general_disponibles" if tipo == "general" else "asientos_premium_disponibles"
    campo_precio = "precio_general" if tipo == "general" else "precio_premium"

    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT f.{campo_asientos}, f.{campo_precio},
                           p.titulo, f.fecha, f.hora, s.nombre
                    FROM funciones f
                    JOIN peliculas p ON f.pelicula_id = p.id
                    JOIN salas s ON f.sala_id = s.id
                    WHERE f.id = %s
                    """,
                    (funcion_id,),
                )
                row = cur.fetchone()

                if not row:
                    return f"No existe una función con ID {funcion_id}. Consultá la cartelera para obtener el ID correcto."

                asientos_disp, precio_unitario, titulo, fecha, hora, sala = row

                if asientos_disp < cantidad:
                    return (
                        f"No hay suficientes lugares {tipo} disponibles. "
                        f"Quedan {asientos_disp} para {titulo} ({hora})."
                    )

                codigo = _generar_codigo()
                session_id = current_session_id.get()

                cur.execute(
                    f"UPDATE funciones SET {campo_asientos} = {campo_asientos} - %s WHERE id = %s",
                    (cantidad, funcion_id),
                )
                cur.execute(
                    """
                    INSERT INTO reservas (codigo, session_id, funcion_id, cantidad_entradas, tipo_entrada)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (codigo, session_id, funcion_id, cantidad, tipo),
                )

        hora_str = hora.strftime("%H:%M") if hasattr(hora, "strftime") else str(hora)[:5]
        fecha_str = fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha)
        total = precio_unitario * cantidad

        return (
            f"✅ RESERVA CONFIRMADA\n"
            f"Código: {codigo}\n"
            f"Película: {titulo}\n"
            f"Fecha: {fecha_str} a las {hora_str} — {sala}\n"
            f"Entradas: {cantidad}x {tipo} (${precio_unitario:.0f} c/u)\n"
            f"Total: ${total:.0f}\n"
            f"Presentá este código en boletería."
        )

    except Exception as e:
        return f"Error al crear la reserva: {e}"


@tool
def consultar_reserva(codigo: str) -> str:
    """
    Consulta el estado de una reserva existente por su código.

    Usá esta herramienta cuando el usuario quiera verificar o recordar los datos de una reserva.

    Args:
        codigo: Código de reserva (ej: CIN-AB12CD)
    """
    print(f"   🔍 Consultando reserva: {codigo}")

    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT r.codigo, r.cantidad_entradas, r.tipo_entrada, r.estado,
                           p.titulo, f.fecha, f.hora, s.nombre
                    FROM reservas r
                    JOIN funciones f ON r.funcion_id = f.id
                    JOIN peliculas p ON f.pelicula_id = p.id
                    JOIN salas s ON f.sala_id = s.id
                    WHERE UPPER(r.codigo) = UPPER(%s)
                    """,
                    (codigo.strip(),),
                )
                row = cur.fetchone()

        if not row:
            return f"No se encontró ninguna reserva con el código {codigo.upper()}."

        codigo_r, cantidad, tipo, estado, titulo, fecha, hora, sala = row
        hora_str = hora.strftime("%H:%M") if hasattr(hora, "strftime") else str(hora)[:5]
        fecha_str = fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha)

        return (
            f"Reserva {codigo_r} — {estado.upper()}\n"
            f"Película: {titulo}\n"
            f"Fecha: {fecha_str} a las {hora_str} | {sala}\n"
            f"Entradas: {cantidad}x {tipo}"
        )

    except Exception as e:
        return f"Error al consultar la reserva: {e}"


@tool
def cancelar_reserva(codigo: str) -> str:
    """
    Cancela una reserva existente y libera los asientos.

    Usá esta herramienta SOLO cuando el usuario haya confirmado explícitamente que quiere cancelar.
    Nunca canceles sin confirmación previa del usuario.

    Args:
        codigo: Código de reserva (ej: CIN-AB12CD)
    """
    print(f"   ❌ Cancelando reserva: {codigo}")

    try:
        with _get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT r.id, r.funcion_id, r.cantidad_entradas, r.tipo_entrada, r.estado,
                           p.titulo, f.fecha, f.hora
                    FROM reservas r
                    JOIN funciones f ON r.funcion_id = f.id
                    JOIN peliculas p ON f.pelicula_id = p.id
                    WHERE UPPER(r.codigo) = UPPER(%s)
                    """,
                    (codigo.strip(),),
                )
                row = cur.fetchone()

                if not row:
                    return f"No se encontró ninguna reserva con el código {codigo.upper()}."

                reserva_id, funcion_id, cantidad, tipo, estado, titulo, fecha, hora = row

                if estado == "cancelada":
                    return f"La reserva {codigo.upper()} ya estaba cancelada."
                if estado == "usada":
                    return f"La reserva {codigo.upper()} ya fue utilizada y no puede cancelarse."

                campo_asientos = (
                    "asientos_general_disponibles"
                    if tipo == "general"
                    else "asientos_premium_disponibles"
                )

                cur.execute(
                    f"UPDATE funciones SET {campo_asientos} = {campo_asientos} + %s WHERE id = %s",
                    (cantidad, funcion_id),
                )
                cur.execute(
                    "UPDATE reservas SET estado = 'cancelada' WHERE id = %s",
                    (reserva_id,),
                )

        hora_str = hora.strftime("%H:%M") if hasattr(hora, "strftime") else str(hora)[:5]
        fecha_str = fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha)

        return (
            f"✅ Reserva {codigo.upper()} cancelada correctamente.\n"
            f"Película: {titulo} — {fecha_str} a las {hora_str}\n"
            f"Se liberaron {cantidad} asiento(s) {tipo}."
        )

    except Exception as e:
        return f"Error al cancelar la reserva: {e}"
