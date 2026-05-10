# CineBot — Roadmap de producto

Ideas y mejoras discutidas para evolucionar CineBot como servicio para cines.

---

## Implementado

- [x] **Cancelación de reservas** — Tool `cancelar_reserva` con confirmación explícita y rollback de asientos
- [x] **Sugerencia de menú pre-reserva** — Upsell contextual (hora, cantidad, género) antes de ejecutar `crear_reserva`
- [x] **Fecha en cartelera** — El bot siempre incluye la fecha al mostrar funciones
- [x] **Verificación de funcion_id** — El agente valida que el ID corresponde exactamente a la película y horario pedidos antes de reservar

---

## Próximas mejoras de experiencia

### Streaming de respuestas
El bot responde mientras genera, en lugar de esperar la respuesta completa. Reduce la percepción de latencia de 3-5 segundos a casi cero.
- FastAPI: `StreamingResponse` con `text/event-stream`
- LangChain: `.astream()` en lugar de `.invoke()`
- Frontend: consumir el stream con `ReadableStream` y actualizar el mensaje en tiempo real

### Recordatorio antes de la función
Chatwoot envía un mensaje automático ~90 minutos antes de la función reservada.
- Requiere: job scheduler (APScheduler o Celery) que revise reservas próximas cada X minutos
- Mensaje tipo: "Tu función de Thunderbolts* empieza en 90 minutos. Código: CIN-RMWFMD. ¡Buen cine!"
- Dispara desde el backend usando la API de Chatwoot (`POST /api/v1/accounts/{id}/conversations/{id}/messages`)

---

## Para ofrecer como servicio (B2B)

### Panel de administración
Interfaz web para que el cine gestione su cartelera sin tocar SQL.
- CRUD de películas (título, género, duración, clasificación, activa/inactiva)
- CRUD de salas
- Gestión de funciones (fecha, hora, sala, precios, asientos)
- Vista de reservas del día
- Stack sugerido: Next.js + Supabase Auth + las mismas tablas existentes

### Multi-tenant
Permitir que múltiples cines usen la misma plataforma con datos aislados.
- Agregar columna `tenant_id` a todas las tablas operacionales
- Row Level Security en Supabase por tenant
- Cada cine tiene su propio Chatwoot inbox y bot label
- Variables de entorno o tabla de configuración por tenant (nombre del cine, logo, timezone)

### Analytics para el cine
Dashboard de métricas que justifica el costo del servicio.
- Reservas por día / semana / película
- Películas más consultadas (no solo reservadas)
- Tasa de conversión: consulta → reserva
- Horario de mayor actividad del chat
- Combos de menú más sugeridos
- Stack: Supabase + una tabla de eventos, visualización con Recharts o Metabase

---

## Funcionalidades avanzadas

### Notas de voz por WhatsApp
El webhook de Chatwoot recibe mensajes de audio → Whisper (OpenAI) transcribe → el agente responde → opcionalmente responde también en audio con TTS.
- Chatwoot ya recibe adjuntos de audio de WhatsApp
- Whisper: `openai.audio.transcriptions.create()`
- TTS: `openai.audio.speech.create()` o ElevenLabs para voz más natural

### Recomendaciones proactivas
El bot contacta primero en lugar de esperar al usuario.
- Viernes a la tarde: "Esta semana llega Superman. La última vez que fuiste viste algo de superhéroes, puede interesarte."
- Usa el historial de conversación (PostgreSQL) para personalizar
- Requiere job scheduler + Chatwoot API para iniciar conversaciones

### Rating post-película
24 horas después de una función, el bot pregunta cómo estuvo.
- "¿Cómo te fue con Thunderbolts*? ¿La recomendarías?"
- Los ratings se guardan en una tabla `ratings` y alimentan las recomendaciones del RAG
- Cierra el loop: reserva → experiencia → feedback → mejor recomendación futura
