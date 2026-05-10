"""
Carga inicial de la base de conocimiento de CineBot en Supabase.
Editá PELICULAS con tus propias fichas y ejecutá:

    python seed_conocimiento.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from langchain_core.documents import Document
from tools.Base_de_conocimiento import vectorstore

# ============================================================
# FICHAS DE PELÍCULAS — ESTRENOS 2025/2026
# ============================================================
PELICULAS = [
    """
Título: Avengers: Doomsday
Género: Acción / Ciencia Ficción / Superhéroes
Duración: estimada 150 minutos
Clasificación: Apta para mayores de 13 años
Dirección: Anthony y Joe Russo
Reparto: Robert Downey Jr. (Doctor Doom), Anthony Mackie (Captain America), Pedro Pascal, Florence Pugh, Sebastian Stan, entre otros
Año: 2026
Sinopsis: Los Vengadores se enfrentan a su amenaza más poderosa hasta el momento: Victor Von Doom, también conocido como Doctor Doom, interpretado por Robert Downey Jr. en un regreso inesperado al MCU. El destino de la realidad misma está en juego en este evento cinematográfico que reúne a héroes de múltiples películas.
Tono: Épica, oscura y con momentos de tensión máxima. Exige haber visto varias películas del MCU para entender todas las referencias. Para fans de los Vengadores es un evento imperdible.
Curiosidades: Marca el regreso de los directores Russo al MCU. Robert Downey Jr. vuelve pero como el villano, no como Iron Man.
""",
    """
Título: Misión Imposible: El Ajuste Final
Título original: Mission: Impossible – The Final Reckoning
Género: Acción / Espionaje / Thriller
Duración: 169 minutos
Clasificación: Apta para mayores de 13 años
Dirección: Christopher McQuarrie
Reparto: Tom Cruise (Ethan Hunt), Hayley Atwell, Simon Pegg, Ving Rhames, Esai Morales, Vanessa Kirby
Año: 2025
Sinopsis: Ethan Hunt y su equipo llegan a la misión definitiva: detener a la Entidad, una inteligencia artificial sin control que amenaza el equilibrio global. Con escenas de acción práctica extrema y un ritmo que no da respiro, es la conclusión de una de las sagas más adrenalínicas del cine.
Tono: Vertiginosa, espectacular y con momentos emotivos. La secuencia de apertura ya es una de las más impresionantes del cine de acción reciente.
Curiosidades: Tom Cruise realizó las acrobacias sin doble, incluyendo una secuencia submarina de larga duración.
""",
    """
Título: Minecraft: La Película
Título original: A Minecraft Movie
Género: Aventura / Comedia / Familiar / Animación live-action
Duración: 101 minutos
Clasificación: Apta para todo público
Dirección: Jared Hess
Reparto: Jack Black (Steve), Jason Momoa, Jennifer Coolidge, Emma Myers
Año: 2025
Sinopsis: Cuatro inadaptados se ven arrastrados al Submundo, el universo pixelado de Minecraft. Para volver a casa deberán sobrevivir a criaturas, explorar biomas y dominar las mecánicas del juego en un mundo literal hecho de bloques. Con humor absurdo y mucha acción.
Tono: Desopilante, visualmente original y muy entretenida para todas las edades. Los adultos disfrutan de Jack Black tanto como los chicos de los guiños al juego.
Curiosidades: Fue el estreno más taquillero del año en su semana de debut. Jack Black insistió en hacer el personaje físicamente el mismo.
""",
    """
Título: Thunderbolts*
Género: Acción / Superhéroes / Drama psicológico
Duración: 127 minutos
Clasificación: Apta para mayores de 13 años
Dirección: Jake Schreier
Reparto: Florence Pugh (Yelena Belova), Sebastian Stan (Bucky Barnes), Wyatt Russell (John Walker), David Harbour (Red Guardian), Hannah John-Kamen, Julia Louis-Dreyfus
Año: 2025
Sinopsis: Un grupo de antihéroes con pasados oscuros y traumas sin resolver es reclutado para una misión que ningún superhéroe convencional aceptaría. A medida que operan juntos descubren que su mayor enemigo puede estar dentro de ellos mismos. El asterisco del título tiene un significado que el film revela.
Tono: Más íntima y psicológica que el promedio del MCU. Florence Pugh lleva el film con una actuación destacada. Para los que disfrutan de superhéroes con matices.
Curiosidades: Es una de las películas del MCU más aclamadas por la crítica en años por apartarse de la fórmula habitual.
""",
    """
Título: Superman
Género: Acción / Aventura / Superhéroes
Duración: 129 minutos
Clasificación: Apta para mayores de 13 años
Dirección: James Gunn
Reparto: David Corenswet (Clark Kent / Superman), Rachel Brosnahan (Lois Lane), Nicholas Hoult (Lex Luthor), Edi Gathegi (Mister Terrific)
Año: 2025
Sinopsis: El reinicio del universo DC bajo James Gunn presenta a un Clark Kent joven que aún está aprendiendo a equilibrar su humanidad con sus poderes kryptonianos. Más esperanzadora y colorida que las versiones anteriores, con un tono que recupera el espíritu optimista del personaje original.
Tono: Luminosa, emotiva y con humor justo. Gunn recupera la esencia del Superman de los cómics: un héroe que inspira, no que aterra.
Curiosidades: Es el primer film del nuevo DC Universe (DCU). James Gunn tiene el control creativo total de esta nueva etapa de DC.
""",
    """
Título: Wicked: El Bien Triunfará
Título original: Wicked: For Good
Género: Musical / Fantasía / Drama
Duración: 160 minutos
Clasificación: Apta para todo público
Dirección: Jon M. Chu
Reparto: Cynthia Erivo (Elphaba), Ariana Grande (Glinda), Jonathan Bailey, Jeff Goldblum (El Mago)
Año: 2025
Sinopsis: La segunda y última parte de la adaptación del musical más exitoso de Broadway. Elphaba y Glinda llegan al punto de quiebre de su amistad mientras el mundo de Oz se acerca a la confrontación final. Incluye las canciones más icónicas del show, incluyendo "For Good" y "Defying Gravity" en su contexto completo.
Tono: Emotiva, visualmente impactante y musicalmente poderosa. Cierra el arco de personajes con fuerza. Recomendada incluso para quienes no son fans habituales de los musicales.
Curiosidades: Ariana Grande describió el proyecto como el rol de su vida. Cynthia Erivo recibió críticas unánimes por su interpretación de Elphaba.
""",
]

# ============================================================
# CARGA EN SUPABASE
# ============================================================
def main():
    print(f"📚 Cargando {len(PELICULAS)} películas en la base de conocimiento...")

    documentos = [
        Document(page_content=ficha.strip(), metadata={"fuente": "ficha_manual"})
        for ficha in PELICULAS
    ]

    ids = vectorstore.add_documents(documentos)
    print(f"✅ {len(ids)} documentos cargados correctamente.")
    print("   Ya podés preguntarle a CineBot sobre estas películas.")


if __name__ == "__main__":
    main()
