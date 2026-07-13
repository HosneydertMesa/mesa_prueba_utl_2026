# Seguridad del proyecto

## Secretos

- No almacenar tokens, contraseñas, cookies o cabeceras privadas.
- Autenticar GitHub mediante `gh auth login` cuando se autorice la publicación.
- Usar credenciales nuevas, de alcance mínimo y con expiración.
- Revocar inmediatamente cualquier credencial compartida por chat, logs o commits.
- Antes de publicar, ejecutar `python scripts/quality_gate.py sec` y revisar el historial completo.

## Datos y API

- El PDF confidencial permanece fuera del repositorio.
- Solo se consumen endpoints públicos observados.
- Toda petición usa timeout, retry limitado y backoff.
- Los logs no imprimen cabeceras sensibles ni payloads completos.
- Las consultas Python-SQL usan placeholders para valores.

## Reporte local

Si se detecta un secreto, detener publicación, revocarlo, retirar el valor de archivos e historial y volver a ejecutar la puerta SEC.

