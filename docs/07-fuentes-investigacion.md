# Fuentes de investigación y decisiones derivadas

Consultadas y actualizadas al 13 de julio de 2026. Se priorizan fuentes oficiales
y se registran solo decisiones aplicables al alcance.

| Fuente | Evidencia relevante | Aplicación en el proyecto |
|---|---|---|
| [Portal oficial de resultados 2026](https://resultadospreccongreso2026.registraduria.gov.co/) | El portal existe, pero su aplicación no expone un contrato indexable estable | Descubrimiento con Network/F12 y fixtures; no adivinar endpoints |
| [SQLite: foreign keys](https://www.sqlite.org/foreignkeys.html) | Las FK deben habilitarse por conexión; índices en claves hijas evitan escaneos | `PRAGMA foreign_keys=ON`, `foreign_key_check` e índices justificados |
| [SQLite: ON CONFLICT](https://www.sqlite.org/lang_conflict.html) | `IGNORE` aplica a restricciones seleccionadas, no a FK | Usar `INSERT OR IGNORE` solo con `UNIQUE` correcto; no ocultar integridad |
| [SQLite: CREATE INDEX](https://www.sqlite.org/lang_createindex.html) | Los índices deben corresponder a patrones reales de consulta | Justificar 3+ índices con SQL objetivo y `EXPLAIN QUERY PLAN` |
| [Python: sqlite3](https://docs.python.org/3/library/sqlite3.html) | Transacciones y parámetros tienen semántica explícita; concatenar SQL es inseguro | Contextos transaccionales y placeholders, nunca interpolación de valores |
| [Modelo de incidencia citado por la prueba](https://github.com/willamaya/Insidencia-Electoral) | Publica homologación CA→SE y atribución mesa a mesa | CTE explícito con códigos y pesos; no se adivinan equivalencias de coalición |
| [scikit-learn: validación agrupada](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data) | La independencia se rompe con muestras del mismo grupo | Agrupar por municipio/puesto; no separar mesas relacionadas al azar |
| [scikit-learn: GroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html) | Evita que un grupo aparezca en entrenamiento y prueba a la vez | Sensibilidad leave-one-municipality-out con cuatro grupos |
| [statsmodels: Cook's distance](https://www.statsmodels.org/stable/generated/statsmodels.stats.outliers_influence.GLMInfluence.cooks_distance.html) | Permite cuantificar influencia sobre el ajuste | Marcar observaciones influyentes sin llamarlas fraude ni eliminarlas automáticamente |
| [`actions/checkout` releases](https://github.com/actions/checkout/releases) y [`actions/setup-python` releases](https://github.com/actions/setup-python/releases) | Los majors basados en Node 24 sustituyen runtimes Node 20 en deprecación | Usar `checkout@v7` y `setup-python@v6` conservando Python explícito y gates |
| [`actions/configure-pages` releases](https://github.com/actions/configure-pages/releases), [`actions/upload-pages-artifact` releases](https://github.com/actions/upload-pages-artifact/releases) y [`actions/deploy-pages` releases](https://github.com/actions/deploy-pages/releases) | Los majors vigentes migran a Node 24 y mantienen el flujo oficial de Pages | Usar v6/v5/v5, permisos mínimos, artefacto estático y smoke HTTPS posterior |

## Conclusión de investigación

El mayor diferenciador no es un algoritmo más complejo: es demostrar integridad, reproducibilidad, validación sin fuga entre grupos y una lectura estadística honesta. Ridge se conserva como comparación opcional; árboles o boosting quedan fuera salvo que nuevos datos y una pregunta predictiva real los justifiquen.
