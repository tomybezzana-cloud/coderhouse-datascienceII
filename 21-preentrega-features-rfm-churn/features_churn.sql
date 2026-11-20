-- =============================================================================
-- Pre-entrega 7: ingeniería de features con SQL analítico para predecir churn
-- Autor: Tomás Bezzana
--
-- Motor: DuckDB. Ejecutar desde esta carpeta:
--   python ejecutar.py            (recomendado: imprime cada resultado)
--   duckdb < features_churn.sql   (CLI de DuckDB)
--
-- Entrada:  data/usuarios.csv, data/pedidos.csv  (crudos, ver generar_datos.py)
-- Salida:   tabla features_churn  -> data/features_churn.csv
--           una fila por usuario, lista para entrenar un modelo de churn.
--
-- Regla de oro: todas las features se calculan con datos HASTA la fecha de
-- corte (2025-12-31). Los pedidos posteriores existen en los datos, pero usarlos
-- en una feature sería mirar el futuro (data leakage). Solo se usan, en la
-- sección 3, para construir la etiqueta de churn.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 0. Carga de los datos crudos
-- -----------------------------------------------------------------------------
-- Se declaran los tipos explícitamente en lugar de dejar que DuckDB los
-- adivine, para que fecha_pedido sea DATE y monto sea DECIMAL siempre.
CREATE OR REPLACE TABLE usuarios AS
SELECT *
FROM read_csv('data/usuarios.csv', header = true, columns = {
    'usuario_id':     'INTEGER',
    'fecha_registro': 'DATE'
});

CREATE OR REPLACE TABLE pedidos AS
SELECT *
FROM read_csv('data/pedidos.csv', header = true, columns = {
    'pedido_id':    'INTEGER',
    'usuario_id':   'INTEGER',
    'fecha_pedido': 'DATE',
    'monto':        'DECIMAL(10, 2)',
    'estado':       'VARCHAR'
});

-- Consulta: 0. Datos crudos cargados
SELECT
    (SELECT COUNT(*) FROM usuarios)                                   AS usuarios,
    COUNT(*)                                                          AS pedidos_totales,
    COUNT(*) FILTER (WHERE estado = 'cancelado')                      AS pedidos_cancelados,
    COUNT(*) FILTER (WHERE fecha_pedido > DATE '2025-12-31')          AS pedidos_despues_del_corte,
    MIN(fecha_pedido)                                                 AS primer_pedido,
    MAX(fecha_pedido)                                                 AS ultimo_pedido
FROM pedidos;


-- -----------------------------------------------------------------------------
-- 1. Tabla de features (consulta principal)
-- -----------------------------------------------------------------------------
-- Se arma en pasos con CTEs, de lo más crudo a lo más agregado:
--   parametros         fecha de corte y último mes completo.
--   pedidos_validos    filtro de pedidos que cuentan como compra.
--   compras_con_gap    LAG: días entre cada compra y la anterior.
--   resumen_rfm        una fila por usuario: Recency, Frequency, Monetary.
--   meses_usuario      calendario: un mes por usuario desde su registro.
--   gasto_mensual      gasto de cada usuario en cada mes (0 si no compró).
--   tendencia          AVG OVER: promedio histórico y delta del último mes.
-- y al final se unen y se agregan los scores RFM con NTILE.
CREATE OR REPLACE TABLE features_churn AS
WITH
parametros AS (
    SELECT
        DATE '2025-12-31'                                AS fecha_corte,
        -- Último mes COMPLETO antes del corte. Si se comparara un mes a medio
        -- terminar contra meses completos, la tendencia saldría negativa para
        -- todos por construcción.
        CAST(date_trunc('month', DATE '2025-12-31') AS DATE) AS ultimo_mes
),

-- Filtro de negocio: una compra es un pedido COMPLETADO, realizado hasta la
-- fecha de corte. Los cancelados no son gasto real, y los posteriores al
-- corte son el futuro que el modelo tiene que predecir.
pedidos_validos AS (
    SELECT
        ped.pedido_id,
        ped.usuario_id,
        ped.fecha_pedido,
        ped.monto
    FROM pedidos AS ped
    CROSS JOIN parametros AS par
    WHERE ped.estado = 'completado'
      AND ped.fecha_pedido <= par.fecha_corte
),

-- LAG(fecha_pedido) OVER (PARTITION BY usuario_id ORDER BY fecha_pedido)
--   Para cada compra devuelve la fecha de la compra ANTERIOR del mismo usuario.
--   PARTITION BY usuario_id -> la "anterior" se busca solo entre sus compras.
--   ORDER BY fecha_pedido   -> define qué es anterior; pedido_id desempata dos
--                              compras del mismo día.
--   En la primera compra de cada usuario LAG devuelve NULL (no hay anterior).
compras_con_gap AS (
    SELECT
        usuario_id,
        pedido_id,
        fecha_pedido,
        monto,
        date_diff(
            'day',
            LAG(fecha_pedido) OVER (
                PARTITION BY usuario_id
                ORDER BY fecha_pedido, pedido_id
            ),
            fecha_pedido
        )                                                AS dias_desde_compra_anterior
    FROM pedidos_validos
),

-- Una fila por usuario. El LEFT JOIN desde usuarios mantiene a los que nunca
-- compraron (sus columnas de compras quedan en NULL y se resuelven al final).
-- GROUP BY incluye las dos columnas no agregadas del SELECT.
resumen_rfm AS (
    SELECT
        usr.usuario_id,
        usr.fecha_registro,
        MIN(cmp.fecha_pedido)                            AS primera_compra,
        MAX(cmp.fecha_pedido)                            AS ultima_compra,
        COUNT(DISTINCT cmp.pedido_id)                    AS frequency,
        SUM(cmp.monto)                                   AS monetary,
        AVG(cmp.dias_desde_compra_anterior)              AS dias_promedio_entre_compras
    FROM usuarios AS usr
    LEFT JOIN compras_con_gap AS cmp
        ON cmp.usuario_id = usr.usuario_id
    GROUP BY usr.usuario_id, usr.fecha_registro
),

-- Calendario de meses por usuario: desde el mes en que se registró hasta el
-- último mes completo. Arrancar en el registro evita sesgar el promedio
-- histórico con meses en los que el usuario todavía no existía.
meses_usuario AS (
    SELECT
        usr.usuario_id,
        CAST(cal.mes AS DATE)                            AS mes
    FROM usuarios AS usr
    CROSS JOIN parametros AS par
    CROSS JOIN generate_series(
        date_trunc('month', usr.fecha_registro),
        par.ultimo_mes,
        INTERVAL 1 MONTH
    ) AS cal (mes)
),

-- Gasto por usuario y mes. El LEFT JOIN desde el calendario hace que los
-- meses sin compras existan y valgan 0. Sin el calendario, esos meses
-- directamente no aparecerían y el promedio se calcularía solo sobre los
-- meses con compra (inflado).
gasto_mensual AS (
    SELECT
        mes.usuario_id,
        mes.mes,
        COALESCE(SUM(pv.monto), 0)                       AS gasto_mes
    FROM meses_usuario AS mes
    LEFT JOIN pedidos_validos AS pv
        ON  pv.usuario_id = mes.usuario_id
        AND CAST(date_trunc('month', pv.fecha_pedido) AS DATE) = mes.mes
    GROUP BY mes.usuario_id, mes.mes
),

-- AVG(gasto_mes) OVER (PARTITION BY usuario_id ORDER BY mes
--                      ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)
--   PARTITION BY usuario_id -> cada usuario se compara consigo mismo.
--   ORDER BY mes + ROWS ... 1 PRECEDING -> promedia todos los meses ANTERIORES
--   al de la fila, sin incluirla. Así, en la fila del último mes, el promedio
--   histórico no contiene al último mes (si lo incluyera, el delta quedaría
--   achicado hacia 0).
-- La ventana se calcula sobre todos los meses y recién después se filtra el
-- último: si se filtrara antes (en el mismo WHERE), la ventana no vería los
-- meses anteriores.
tendencia_mensual AS (
    SELECT
        usuario_id,
        mes,
        gasto_mes,
        AVG(gasto_mes) OVER (
            PARTITION BY usuario_id
            ORDER BY mes
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        )                                                AS promedio_meses_anteriores
    FROM gasto_mensual
),

tendencia AS (
    SELECT
        tm.usuario_id,
        tm.gasto_mes                                     AS gasto_ultimo_mes,
        -- Un usuario registrado en el último mes no tiene meses anteriores:
        -- su promedio histórico es 0 y su tendencia es todo lo que gastó.
        COALESCE(tm.promedio_meses_anteriores, 0)        AS promedio_mensual_historico
    FROM tendencia_mensual AS tm
    CROSS JOIN parametros AS par
    WHERE tm.mes = par.ultimo_mes
),

features AS (
    SELECT
        rfm.usuario_id,
        date_diff('day', rfm.fecha_registro, par.fecha_corte)     AS antiguedad_dias,
        CASE WHEN rfm.frequency > 0 THEN 1 ELSE 0 END              AS tiene_compras,

        -- Recency: días desde la última compra. Quien nunca compró lleva
        -- inactivo desde que se registró, así que se usa su antigüedad.
        date_diff('day',
                  COALESCE(rfm.ultima_compra, rfm.fecha_registro),
                  par.fecha_corte)                                AS recency_dias,

        rfm.frequency,
        COALESCE(rfm.monetary, 0)                                 AS monetary,
        COALESCE(ROUND(rfm.monetary / NULLIF(rfm.frequency, 0), 2), 0)
                                                                  AS ticket_promedio,

        -- Con 0 o 1 compra no hay intervalo entre compras. Se usa el tiempo
        -- transcurrido desde la primera compra (o desde el registro): el
        -- intervalo real es, como mínimo, ese.
        ROUND(COALESCE(
            rfm.dias_promedio_entre_compras,
            date_diff('day',
                      COALESCE(rfm.primera_compra, rfm.fecha_registro),
                      par.fecha_corte)
        ), 1)                                                     AS dias_promedio_entre_compras,

        tnd.gasto_ultimo_mes,
        ROUND(tnd.promedio_mensual_historico, 2)                  AS promedio_mensual_historico,
        -- Trend: positivo = gastó más que su promedio; negativo = se enfría.
        ROUND(tnd.gasto_ultimo_mes - tnd.promedio_mensual_historico, 2)
                                                                  AS trend_gasto
    FROM resumen_rfm AS rfm
    CROSS JOIN parametros AS par
    LEFT JOIN tendencia AS tnd
        ON tnd.usuario_id = rfm.usuario_id
)

-- Scores RFM con NTILE(5): reparte a los clientes en 5 grupos de igual tamaño
-- según cada métrica (5 = mejor). usuario_id desempata para que el reparto de
-- los empates sea siempre el mismo.
--   r_score: ORDER BY recency DESC -> los más recientes quedan en el grupo 5.
--   f_score / m_score: ORDER BY ASC -> los que más compran/gastan, en el 5.
--   PARTITION BY tiene_compras -> los quintiles se arman SOLO entre clientes.
--   Si se mezclaran los usuarios sin compras (recency = antigüedad), alguien
--   registrado hace poco y que nunca compró quedaría como "reciente". A ellos
--   se les asigna 0: por debajo del peor cliente.
SELECT
    ftr.*,
    CASE WHEN ftr.tiene_compras = 0 THEN 0 ELSE
        NTILE(5) OVER (PARTITION BY ftr.tiene_compras
                       ORDER BY ftr.recency_dias DESC, ftr.usuario_id)
    END                                                              AS r_score,
    CASE WHEN ftr.tiene_compras = 0 THEN 0 ELSE
        NTILE(5) OVER (PARTITION BY ftr.tiene_compras
                       ORDER BY ftr.frequency, ftr.usuario_id)
    END                                                              AS f_score,
    CASE WHEN ftr.tiene_compras = 0 THEN 0 ELSE
        NTILE(5) OVER (PARTITION BY ftr.tiene_compras
                       ORDER BY ftr.monetary, ftr.usuario_id)
    END                                                              AS m_score
FROM features AS ftr
ORDER BY ftr.usuario_id;

-- Consulta: 1. Tabla features_churn (primeros 12 usuarios)
SELECT
    usuario_id,
    antiguedad_dias,
    recency_dias,
    frequency,
    monetary,
    ticket_promedio,
    dias_promedio_entre_compras,
    gasto_ultimo_mes,
    promedio_mensual_historico,
    trend_gasto,
    r_score,
    f_score,
    m_score
FROM features_churn
ORDER BY usuario_id
LIMIT 12;


-- -----------------------------------------------------------------------------
-- 2. Controles de calidad del dataset
-- -----------------------------------------------------------------------------
-- Una fila por usuario (ni duplicados por los JOIN ni usuarios perdidos) y
-- ningún NULL en las features.
-- Consulta: 2. Controles de calidad
SELECT
    COUNT(*)                                              AS filas,
    COUNT(DISTINCT usuario_id)                            AS usuarios_distintos,
    (SELECT COUNT(*) FROM usuarios)                       AS usuarios_en_origen,
    SUM(tiene_compras)                                    AS usuarios_con_compras,
    COUNT(*) - COUNT(recency_dias)
      + COUNT(*) - COUNT(monetary)
      + COUNT(*) - COUNT(dias_promedio_entre_compras)
      + COUNT(*) - COUNT(gasto_ultimo_mes)
      + COUNT(*) - COUNT(trend_gasto)                     AS valores_nulos
FROM features_churn;


-- -----------------------------------------------------------------------------
-- 3. Validación: ¿las features anticipan el churn?
-- -----------------------------------------------------------------------------
-- Etiqueta: un cliente (al menos 1 compra antes del corte) hace churn si NO
-- tiene ninguna compra completada en los 59 días siguientes al corte
-- (2026-01-01 a 2026-02-28). Es el único lugar donde se miran pedidos
-- posteriores al corte, y es justamente lo que el modelo tendría que predecir.
CREATE OR REPLACE TABLE etiqueta_churn AS
SELECT
    ftr.usuario_id,
    CASE WHEN COUNT(ped.pedido_id) = 0 THEN 1 ELSE 0 END    AS churn
FROM features_churn AS ftr
LEFT JOIN pedidos AS ped
    ON  ped.usuario_id = ftr.usuario_id
    AND ped.estado = 'completado'
    AND ped.fecha_pedido BETWEEN DATE '2026-01-01' AND DATE '2026-02-28'
WHERE ftr.tiene_compras = 1
GROUP BY ftr.usuario_id;

-- Promedio de cada feature según la etiqueta. Si las features son útiles,
-- los dos grupos se tienen que ver distintos.
-- Consulta: 3. Promedio de las features según churn
SELECT
    etq.churn,
    COUNT(*)                                              AS clientes,
    ROUND(AVG(ftr.recency_dias), 1)                       AS recency_dias,
    ROUND(AVG(ftr.frequency), 1)                          AS frequency,
    ROUND(AVG(ftr.monetary), 2)                           AS monetary,
    ROUND(AVG(ftr.dias_promedio_entre_compras), 1)        AS dias_entre_compras,
    ROUND(AVG(ftr.trend_gasto), 2)                        AS trend_gasto,
    ROUND(AVG(ftr.r_score), 2)                            AS r_score
FROM etiqueta_churn AS etq
JOIN features_churn AS ftr
    ON ftr.usuario_id = etq.usuario_id
GROUP BY etq.churn
ORDER BY etq.churn;

-- Tasa de churn por r_score: cuanto más reciente la última compra, menos churn.
-- Consulta: 4. Tasa de churn por r_score
SELECT
    ftr.r_score,
    COUNT(*)                                              AS clientes,
    SUM(etq.churn)                                        AS hicieron_churn,
    ROUND(100.0 * AVG(etq.churn), 1)                      AS tasa_churn_pct,
    MIN(ftr.recency_dias)                                 AS recency_min,
    MAX(ftr.recency_dias)                                 AS recency_max
FROM etiqueta_churn AS etq
JOIN features_churn AS ftr
    ON ftr.usuario_id = etq.usuario_id
GROUP BY ftr.r_score
ORDER BY ftr.r_score;


-- -----------------------------------------------------------------------------
-- 4. Error común: no filtrar el período (data leakage)
-- -----------------------------------------------------------------------------
-- Misma Recency y Frequency, pero SIN el filtro fecha_pedido <= fecha_corte.
-- Los clientes que compraron después del corte quedan con recency negativa
-- (su "última compra" es posterior al día de referencia) y con más pedidos de
-- los que existían a esa fecha. Un modelo entrenado así parecería excelente
-- en la validación, porque la feature ya trae escrita la respuesta: si compró
-- en 2026, no hizo churn.
-- Consulta: 5. Error común: features sin filtrar la fecha de corte
WITH sin_filtro_de_corte AS (
    SELECT
        ped.usuario_id,
        date_diff('day', MAX(ped.fecha_pedido), DATE '2025-12-31')   AS recency_con_leakage,
        COUNT(DISTINCT ped.pedido_id)                                AS frequency_con_leakage
    FROM pedidos AS ped
    WHERE ped.estado = 'completado'
    GROUP BY ped.usuario_id
)
SELECT
    COUNT(*)                                                         AS clientes_afectados,
    MIN(sfc.recency_con_leakage)                                     AS recency_minima,
    SUM(sfc.frequency_con_leakage - ftr.frequency)                   AS pedidos_del_futuro_contados,
    SUM(etq.churn)                                                   AS de_ellos_hicieron_churn
FROM sin_filtro_de_corte AS sfc
JOIN features_churn AS ftr
    ON ftr.usuario_id = sfc.usuario_id
JOIN etiqueta_churn AS etq
    ON etq.usuario_id = sfc.usuario_id
WHERE sfc.recency_con_leakage < 0;


-- -----------------------------------------------------------------------------
-- 5. Exportación del dataset de entrenamiento
-- -----------------------------------------------------------------------------
COPY features_churn TO 'data/features_churn.csv' (HEADER, DELIMITER ',');
