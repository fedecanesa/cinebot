-- ============================================================
-- CineBot — Setup completo en Supabase
-- Ejecutar una sola vez en el SQL Editor de Supabase
-- ============================================================

-- ============================================================
-- PARTE 1: Base de conocimiento (RAG con pgvector)
-- ============================================================

-- 1. Habilitar extensión pgvector
create extension if not exists vector;

-- 2. Tabla de documentos para RAG
create table if not exists documentos (
    id        uuid primary key default gen_random_uuid(),
    content   text,
    metadata  jsonb,
    embedding vector(1536)
);

-- 3. Índice para búsqueda rápida por similitud coseno
create index if not exists documentos_embedding_idx
    on documentos using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);

-- 4. Función de búsqueda semántica (llamada desde LangChain)
create or replace function match_documentos (
    query_embedding vector(1536),
    match_count     int     default 5,
    filter          jsonb   default '{}'
)
returns table (
    id         uuid,
    content    text,
    metadata   jsonb,
    similarity float
)
language plpgsql
as $$
begin
    return query
    select
        documentos.id,
        documentos.content,
        documentos.metadata,
        1 - (documentos.embedding <=> query_embedding) as similarity
    from documentos
    where metadata @> filter
    order by documentos.embedding <=> query_embedding
    limit match_count;
end;
$$;

-- ============================================================
-- PARTE 2: Cartelera y Reservas
-- ============================================================

-- 5. Películas
create table if not exists peliculas (
    id             serial primary key,
    titulo         text not null,
    genero         text,
    duracion_min   int,
    clasificacion  text,
    activa         boolean default true,
    created_at     timestamptz default now()
);

-- 6. Salas
create table if not exists salas (
    id      serial primary key,
    nombre  text not null
);

-- 7. Funciones (showtimes)
create table if not exists funciones (
    id                             serial primary key,
    pelicula_id                    int references peliculas(id) on delete cascade,
    sala_id                        int references salas(id) on delete cascade,
    fecha                          date not null,
    hora                           time not null,
    asientos_general_disponibles   int default 80,
    asientos_premium_disponibles   int default 30,
    precio_general                 numeric(8,2) default 2500,
    precio_premium                 numeric(8,2) default 4000,
    created_at                     timestamptz default now()
);

create index if not exists funciones_fecha_idx on funciones(fecha);
create index if not exists funciones_pelicula_idx on funciones(pelicula_id);

-- 8. Reservas
create table if not exists reservas (
    id                serial primary key,
    codigo            text unique not null,
    session_id        text,
    funcion_id        int references funciones(id) on delete restrict,
    cantidad_entradas int not null check (cantidad_entradas between 1 and 10),
    tipo_entrada      text not null check (tipo_entrada in ('general', 'premium')),
    estado            text default 'confirmada' check (estado in ('confirmada', 'cancelada', 'usada')),
    created_at        timestamptz default now()
);

-- ============================================================
-- PARTE 3: Datos de ejemplo (ajustá títulos, salas y fechas)
-- ============================================================

insert into salas (nombre) values
    ('Sala 1 — 2D'),
    ('Sala 2 — 3D'),
    ('Sala 3 — Premium'),
    ('Sala 4 — IMAX')
on conflict do nothing;

insert into peliculas (titulo, genero, duracion_min, clasificacion) values
    ('Avengers: Doomsday',             'Acción / Ciencia Ficción',  150, 'Apta para mayores de 13 años'),
    ('Misión Imposible: El Ajuste Final', 'Acción / Espionaje',     169, 'Apta para mayores de 13 años'),
    ('Minecraft: La Película',         'Aventura / Familiar',       101, 'Apta para todo público'),
    ('Thunderbolts*',                  'Acción / Superhéroes',      127, 'Apta para mayores de 13 años'),
    ('Superman',                       'Acción / Aventura',         129, 'Apta para mayores de 13 años'),
    ('Wicked: El Bien Triunfará',      'Musical / Fantasía',        160, 'Apta para todo público')
on conflict do nothing;

-- Funciones de ejemplo para hoy y mañana
-- NOTA: ajustá las fechas o usá: current_date y current_date + 1
insert into funciones (pelicula_id, sala_id, fecha, hora, asientos_general_disponibles, asientos_premium_disponibles, precio_general, precio_premium)
select
    p.id, s.id, current_date, funcion.hora::time,
    funcion.gen_disp, funcion.prem_disp,
    funcion.precio_gen, funcion.precio_prem
from (values
    ('Avengers: Doomsday',                'Sala 4 — IMAX',    '16:00', 100, 40, 3500, 6000),
    ('Avengers: Doomsday',                'Sala 4 — IMAX',    '20:30', 100, 40, 3500, 6000),
    ('Misión Imposible: El Ajuste Final', 'Sala 1 — 2D',      '14:30',  80, 30, 2500, 4000),
    ('Misión Imposible: El Ajuste Final', 'Sala 2 — 3D',      '18:15',  80, 30, 2800, 4500),
    ('Minecraft: La Película',            'Sala 1 — 2D',      '11:00',  80, 30, 2200, 3500),
    ('Minecraft: La Película',            'Sala 2 — 3D',      '15:00',  80, 30, 2500, 4000),
    ('Thunderbolts*',                     'Sala 3 — Premium', '17:00',  60, 25, 2500, 4000),
    ('Thunderbolts*',                     'Sala 3 — Premium', '21:00',  60, 25, 2500, 4000),
    ('Superman',                          'Sala 1 — 2D',      '19:30',  80, 30, 2500, 4000),
    ('Wicked: El Bien Triunfará',         'Sala 2 — 3D',      '13:00',  80, 30, 2800, 4500),
    ('Wicked: El Bien Triunfará',         'Sala 2 — 3D',      '19:00',  80, 30, 2800, 4500)
) as funcion(titulo, sala, hora, gen_disp, prem_disp, precio_gen, precio_prem)
join peliculas p on p.titulo = funcion.titulo
join salas s on s.nombre = funcion.sala
on conflict do nothing;
