# CineBot - Resumen de Integración y Debugging (09/05/2026)

## Estado del Proyecto
- **Frontend:** React + Vite, widget de Chatwoot cargado globalmente.
- **Backend:** FastAPI, endpoints para Chatwoot, integración con LangChain, OpenAI, Pinecone, Tavily, PostgreSQL.
- **DB:** Esquema creado y seed ejecutado correctamente.
- **Widget Chatwoot:** Aparece, pero no responde con IA (pendiente de debug).

## Puntos Clave de la Conversación
- El widget está bien configurado y el backend tiene las variables de Chatwoot correctas.
- El problema más común es que el webhook de Chatwoot no apunte al backend (/webhook).
- Se puede apuntar el webhook a producción, siempre que el backend sea público y acepte requests.
- CORS debe estar bien configurado si el backend responde a frontend o Chatwoot.
- El flujo esperado es: widget → Chatwoot → webhook backend → IA → Chatwoot → widget.
- El backend responde a /health y la base está poblada.

## Próximos Pasos
1. Verificar/cambiar el webhook en el panel de Chatwoot para que apunte a /webhook del backend (local o producción).
2. Si sigue sin responder, revisar logs del backend para ver si llegan requests.
3. Si el backend está en producción, asegurar que CORS y el endpoint /webhook estén accesibles.

## Variables y Configuración
- **.env frontend:** Website token y base URL de Chatwoot correctos.
- **.env backend:** Variables de Chatwoot, DB y APIs correctas.

## Otros
- Se corrigió el error de "prepared statement already exists" usando conexiones por request y sin prepared statements.
- El seed_data.sql fue ejecutado y validado.

---

Este archivo resume el estado, problemas y soluciones de la integración CineBot + Chatwoot hasta el 09/05/2026. Útil para continuar el trabajo en otra máquina.
