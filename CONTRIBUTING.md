# Guía de contribución local

1. Seleccionar un ítem de `docs/01-trazabilidad-requisitos.md`.
2. Crear una rama corta desde un `main` limpio.
3. Implementar un solo incremento con su prueba.
4. Ejecutar `python scripts/quality_gate.py all`.
5. Revisar `git diff --check` y `git status --short`.
6. Crear un commit local atómico cuando el usuario lo autorice o el incremento esté aceptado.

No configurar `origin`, publicar ramas ni crear repositorios sin autorización explícita.

