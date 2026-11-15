# coderhouse-datascienceII

Repositorio de prácticas del curso de Data Science II (Coderhouse).

Cada práctica vive en su propia carpeta, numerada en el orden en que se fue
cursando, con su propio README explicando el ejercicio y cómo ejecutarlo.

## Prácticas

| # | Tema | Carpeta |
|---|------|---------|
| 1 | Repaso de Python básico (variables, tipos, listas, diccionarios, funciones) | [`01-repaso-python-basico/`](01-repaso-python-basico/) |
| 2 | Análisis SQL sobre una tabla de ventas (SELECT, WHERE, NULL, GROUP BY, HAVING) | [`02-sql-analisis-ventas/`](02-sql-analisis-ventas/) |
| 3 | Diseño de base de datos para una plataforma de cursos online (diagrama ER + conversión a tablas) | [`03-diseno-bd-cursos/`](03-diseno-bd-cursos/) |
| 4 | Diseño de un sistema de adquisición de datos (DAQ) para un sensor de vibración en aerogeneradores | [`04-diseno-adquisicion-datos/`](04-diseno-adquisicion-datos/) |
| 5 | DML: crear, consultar, actualizar y eliminar datos (SELECT, INSERT, UPDATE, DELETE) sobre una tabla de vendedores | [`05-dml-vendedores/`](05-dml-vendedores/) |
| 6 | Pre-entrega 1: diseño de base de datos para una biblioteca universitaria (ERD + normalización 3FN) | [`06-diseno-bd-biblioteca/`](06-diseno-bd-biblioteca/) |
| 7 | TCL: transacciones seguras y ACID (BEGIN, COMMIT, ROLLBACK) sobre una tabla de productos | [`07-tcl-transacciones-productos/`](07-tcl-transacciones-productos/) |
| 8 | Pre-entrega 2: adquisición y normalización con pandas (merge CSV + Excel, limpieza, export a Parquet) | [`08-adquisicion-normalizacion-pandas/`](08-adquisicion-normalizacion-pandas/) |
| 9 | Ciclo de vida de Machine Learning: mapa del flujo para predecir devoluciones en e-commerce (diagrama con bucles de iteración) | [`09-ciclo-vida-ml-devoluciones/`](09-ciclo-vida-ml-devoluciones/) |
| 10 | Aprendizaje supervisado vs. no supervisado: diagnóstico de 4 casos (clasificación, regresión, clustering) | [`10-supervisado-vs-no-supervisado/`](10-supervisado-vs-no-supervisado/) |
| 11 | Pre-entrega 3: propuesta de proyecto de ML para predecir cancelaciones hoteleras (fuente de datos, diccionario, formato) | [`11-preentrega-propuesta-ml-hoteleria/`](11-preentrega-propuesta-ml-hoteleria/) |
| 12 | Pre-entrega 4: extracción de datos vía API (Open-Meteo) con `.env`, manejo de errores y export a CSV | [`12-preentrega-extraccion-api-clima/`](12-preentrega-extraccion-api-clima/) |
| 13 | Procesamiento vectorial para ML: usuarios como vectores, suma, escalado, producto punto y Bag of Words | [`13-representacion-vectorial-ml/`](13-representacion-vectorial-ml/) |
| 14 | Pre-entrega 5: pipeline ETL modular (`main.py` + `src/`) para reservas hoteleras: tipos optimizados, duplicados, nulos y export a Parquet | [`14-preentrega-pipeline-etl-hoteleria/`](14-preentrega-pipeline-etl-hoteleria/) |
| 15 | SQL aplicado al análisis exploratorio: alias, filtrado y orden, `LIMIT`, `GROUP BY` + `HAVING` sobre `ventas_retail` | [`15-sql-analisis-exploratorio-retail/`](15-sql-analisis-exploratorio-retail/) |
| 16 | Ejecución eficiente de queries analíticas: consulta ingenua vs. optimizada (`SELECT *`, filtros sargables, EXPLAIN, impacto en RAM) | [`16-optimizacion-queries-analiticas/`](16-optimizacion-queries-analiticas/) |
| 17 | Pre-entrega 6: análisis de datos meteorológicos (NOAA, 8 estaciones argentinas) con DuckDB consultando CSV directamente | [`17-preentrega-duckdb-clima/`](17-preentrega-duckdb-clima/) |
| 18 | Funciones de ventana sobre pedidos: promedio por cliente (`PARTITION BY`), ventas acumuladas (`ORDER BY` + `ROWS`) y % de la categoría, sin `GROUP BY` | [`18-funciones-ventana-pedidos/`](18-funciones-ventana-pedidos/) |
| 19 | Tabla maestra de features de clientes para ML: `LEFT JOIN` de 4 tablas, agregación condicionada (`SUM(CASE WHEN)`), `HAVING` y ranking por ciudad con `RANK() OVER` | [`19-features-ml-clientes/`](19-features-ml-clientes/) |
