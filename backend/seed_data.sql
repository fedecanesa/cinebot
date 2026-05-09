-- ============================================================
-- SEED DATA — CineBot
-- Ejecutar después de crear las tablas del schema
-- ============================================================

-- Salas
INSERT INTO salas (nombre, capacidad_general, capacidad_premium) VALUES
  ('Sala 1',   100, 0),
  ('Sala 2',    80, 0),
  ('Sala 3',    60, 20),
  ('Sala VIP',   0, 40);

-- Películas (estrenos y cartelera actual — mayo 2026)
INSERT INTO peliculas (titulo, genero, duracion_min, sinopsis, clasificacion) VALUES
  (
    'Thunderbolts*',
    'Acción / Superhéroes',
    127,
    'Un grupo de antihéroes y villanos reformados es reclutado por una agencia secreta del gobierno para llevar a cabo misiones imposibles que los Avengers no pueden hacer. Acción del universo Marvel con mucho humor negro.',
    '+13'
  ),
  (
    'A Minecraft Movie',
    'Aventura / Animación',
    101,
    'Cuatro inadaptados son transportados al mundo cúbico de Minecraft, donde deberán dominar el entorno para regresar al mundo real. Repleta de humor y referencias al juego.',
    'ATP'
  ),
  (
    'Sinners',
    'Terror / Drama',
    137,
    'Dos hermanos gemelos regresan a su tierra natal en el sur profundo de los años 30 para empezar de cero. Lo que no saben es que han traído algo oscuro consigo. Una historia de vampiros con alma de blues.',
    '+16'
  ),
  (
    'Mickey 17',
    'Ciencia Ficción / Comedia',
    137,
    'Un empleado desechable en una misión de colonización espacial es enviado a morir una y otra vez, siendo clonado cada vez. Pero cuando el clon 17 aparece junto al 18, los dos deben sobrevivir el uno al otro.',
    '+13'
  ),
  (
    'Flow',
    'Animación / Aventura',
    84,
    'Un gato solitario sobrevive en un mundo inundado navegando con animales de otras especies. Sin diálogos, solo imágenes y emoción pura. Ganadora del Oscar a Mejor Película Animada 2025.',
    'ATP'
  ),
  (
    'El Brutalista',
    'Drama',
    215,
    'Un arquitecto judío húngaro llega a Estados Unidos tras la Segunda Guerra Mundial para reconstruir su vida y su arte. Una épica de tres horas y media sobre inmigración, ambición y creatividad. Ganadora del Oscar a Mejor Película 2025.',
    '+16'
  );

-- ============================================================
-- FUNCIONES — próximos 3 días
-- ============================================================

-- Hoy
INSERT INTO funciones (pelicula_id, sala_id, fecha, hora, asientos_general_disponibles, asientos_premium_disponibles, precio_general, precio_premium) VALUES
  -- Thunderbolts*
  (1, 1, CURRENT_DATE, '14:00', 80,  0, 3500, NULL),
  (1, 1, CURRENT_DATE, '17:00', 90,  0, 3500, NULL),
  (1, 3, CURRENT_DATE, '20:00', 50, 18, 3500, 5500),
  (1, 3, CURRENT_DATE, '23:00', 55, 20, 3500, 5500),
  -- A Minecraft Movie
  (2, 2, CURRENT_DATE, '13:30', 70,  0, 3000, NULL),
  (2, 2, CURRENT_DATE, '16:00', 75,  0, 3000, NULL),
  (2, 2, CURRENT_DATE, '18:30', 60,  0, 3000, NULL),
  -- Sinners
  (3, 4, CURRENT_DATE, '19:00',  0, 35, NULL, 6000),
  (3, 4, CURRENT_DATE, '22:30',  0, 38, NULL, 6000),
  -- Mickey 17
  (4, 1, CURRENT_DATE, '21:30', 85,  0, 3500, NULL),
  -- Flow
  (5, 2, CURRENT_DATE, '15:00', 78,  0, 2800, NULL),
  -- El Brutalista
  (6, 3, CURRENT_DATE, '18:00', 55, 20, 4000, 6500);

-- Mañana
INSERT INTO funciones (pelicula_id, sala_id, fecha, hora, asientos_general_disponibles, asientos_premium_disponibles, precio_general, precio_premium) VALUES
  (1, 1, CURRENT_DATE + 1, '14:00', 100,  0, 3500, NULL),
  (1, 1, CURRENT_DATE + 1, '17:30', 100,  0, 3500, NULL),
  (1, 3, CURRENT_DATE + 1, '20:30',  60, 20, 3500, 5500),
  (2, 2, CURRENT_DATE + 1, '15:00',  80,  0, 3000, NULL),
  (2, 2, CURRENT_DATE + 1, '17:30',  80,  0, 3000, NULL),
  (3, 4, CURRENT_DATE + 1, '20:00',   0, 40, NULL, 6000),
  (4, 1, CURRENT_DATE + 1, '21:00',  90,  0, 3500, NULL),
  (5, 2, CURRENT_DATE + 1, '13:00',  80,  0, 2800, NULL),
  (6, 3, CURRENT_DATE + 1, '17:00',  60, 20, 4000, 6500);

-- Pasado mañana
INSERT INTO funciones (pelicula_id, sala_id, fecha, hora, asientos_general_disponibles, asientos_premium_disponibles, precio_general, precio_premium) VALUES
  (1, 1, CURRENT_DATE + 2, '16:00', 100,  0, 3500, NULL),
  (1, 3, CURRENT_DATE + 2, '19:30',  60, 20, 3500, 5500),
  (2, 2, CURRENT_DATE + 2, '14:30',  80,  0, 3000, NULL),
  (3, 4, CURRENT_DATE + 2, '21:00',   0, 40, NULL, 6000),
  (4, 1, CURRENT_DATE + 2, '20:00',  90,  0, 3500, NULL),
  (5, 2, CURRENT_DATE + 2, '12:30',  80,  0, 2800, NULL),
  (6, 3, CURRENT_DATE + 2, '16:30',  60, 20, 4000, 6500);
