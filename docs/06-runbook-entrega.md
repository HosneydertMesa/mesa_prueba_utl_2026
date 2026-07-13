# Runbook de ejecución y entrega

## Desarrollo incremental

1. Incorporar solo insumos autorizados en `sample_data/` y `outputs/`.
2. Crear entorno e instalar dependencias.
3. Ejecutar `--preflight`; registrar cobertura sin escribir BD.
4. Ejecutar scraper y ETL para Tunja; repetir y confirmar cero duplicados.
5. Escalar a Paipa, Sogamoso y Duitama.
6. Ejecutar SQL y revisar muestras calculables manualmente.
7. Exportar JSON; abrir dashboard desde disco y revisar consola.
8. Generar PNG; validar peso, rótulos, valores y stdout.
9. Ejecutar pruebas, verificador y manifest oficial.

## Ensayo de clon limpio

- Clonar en otra carpeta y seguir solo el README con cronómetro de 10 minutos.
- Registrar comandos, tiempos y conocimiento implícito.
- Corregir y repetir hasta pasar.

## Checklist final irreversible

- Sustituir `APELLIDO`, nombre, email y URL; no dejar `PENDIENTE`.
- Manifest: 4/4 municipios y SQL OK x3.
- PNG >10 KB; BD o Release según tamaño.
- Dashboard en Chrome y Firefox, consola limpia.
- Revisar secretos, PDF confidencial y rutas obligatorias.
- Commit final, push a `main`, repo público e incógnito.
- Guardar SHA y URL; enviar el formulario una sola vez antes del cierre.

## Recuperación

- API caída: usar muestras, conservar log y documentar intento.
- SQL ERROR: ejecutar contra copia de BD, corregir y regenerar manifest.
- DB grande: ignorar, subir Release asset y enlazarlo.
- Fallo GitHub en últimos 30 minutos: conservar evidencia y contactar al equipo con el asunto indicado.

