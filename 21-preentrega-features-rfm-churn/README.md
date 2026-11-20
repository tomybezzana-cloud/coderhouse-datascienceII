# Pre-entrega 7: ingeniería de features con SQL analítico para predecir churn

**Autor:** Tomás Bezzana

Transformación de datos crudos de un e-commerce (usuarios y pedidos) en un
**dataset de entrenamiento** con una fila por usuario y features de comportamiento
(Recency, Frequency, Monetary, Trend y otras), listo para un modelo que prediga el
**abandono de clientes (churn)**. Todo el procesamiento se hace con SQL en DuckDB,
con funciones de ventana, agregaciones y filtros por período.

## Archivos

| Archivo | Qué contiene |
|---------|--------------|
| [`features_churn.sql`](features_churn.sql) | **Script principal.** Carga los CSV, genera la tabla de features, corre controles de calidad, valida las features contra una etiqueta de churn y exporta el dataset |
| [`ejecutar.py`](ejecutar.py) | Corre el `.sql` con DuckDB e imprime cada resultado |
| [`generar_datos.py`](generar_datos.py) | Genera los datos crudos sintéticos (semilla fija, siempre los mismos) |
| [`data/usuarios.csv`](data/usuarios.csv), [`data/pedidos.csv`](data/pedidos.csv) | Datos crudos: 60 usuarios y 448 pedidos |
| [`data/features_churn.csv`](data/features_churn.csv) | **Salida:** el dataset de features (60 filas × 14 columnas) |

## Cómo ejecutarlo

```bash
python -m venv .venv
.venv\Scripts\activate             # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python ejecutar.py
```

También corre con la CLI de DuckDB desde esta carpeta: `duckdb < features_churn.sql`.
Los datos crudos ya están en `data/`. Si se borran, `ejecutar.py` los regenera.

## Datos

| Tabla | Columnas |
|-------|----------|
| `usuarios` | `usuario_id`, `fecha_registro` |
| `pedidos` | `pedido_id`, `usuario_id`, `fecha_pedido`, `monto`, `estado` (`completado` / `cancelado`) |

Los pedidos van desde enero de 2025 hasta febrero de 2026. Los usuarios siguen
cinco perfiles de comportamiento: activos, en declive, que abandonaron a mitad de
año, nuevos y sin compras. El perfil **no** está en los datos: la idea es que las
features lo descubran solas a partir de los pedidos.

## La decisión clave: una fecha de corte

Todas las features se calculan "como si hoy fuera" el **31/12/2025**. El modelo va a
usarse para predecir quién va a abandonar a partir de lo que se sabe hoy, así que
al entrenar no puede ver nada posterior a esa fecha. El filtro que lo garantiza es
el mismo para todas las features:

```sql
WHERE ped.estado = 'completado'          -- un cancelado no es gasto real
  AND ped.fecha_pedido <= par.fecha_corte -- nada del futuro
```

Los 65 pedidos de enero y febrero de 2026 se usan **solo** para construir la
etiqueta de churn (sección 3 del script). La consulta 5 muestra qué pasa si se
olvida el filtro: 33 clientes quedan con recency negativa (hasta −59 días, es decir,
"compraron en el futuro") y **ninguno** de ellos hizo churn. La feature ya trae
la respuesta escrita (*data leakage*): el modelo parecería excelente en la
validación y fallaría en producción.

## Features generadas

| Feature | Cómo se calcula | Por qué sirve para predecir churn |
|---------|-----------------|------------------------------------|
| `antiguedad_dias` | Días entre el registro y el corte | Le da contexto al resto. 3 compras no significan lo mismo en un usuario de 2 meses que en uno de 1 año |
| `tiene_compras` | 1 si compró al menos una vez | Separa a los usuarios que nunca se convirtieron en clientes, que son un problema distinto del abandono |
| **`recency_dias`** (R) | `date_diff('day', MAX(fecha_pedido), fecha_corte)` | Es la señal de churn más directa: cuanto más tiempo pasó desde la última compra, más probable es que el cliente ya se haya ido |
| **`frequency`** (F) | `COUNT(DISTINCT pedido_id)` | Un cliente con muchas compras tiene un hábito armado y le cuesta más irse |
| **`monetary`** (M) | `SUM(monto)` | El valor del cliente. No predice el churn por sí solo, pero indica cuánto se pierde si se va y ayuda a priorizar acciones de retención |
| `ticket_promedio` | `monetary / frequency` | Distingue a quien compra poco pero caro de quien compra seguido y barato |
| `dias_promedio_entre_compras` | Promedio de `LAG(fecha_pedido)` dentro de cada usuario | El ritmo habitual de compra. 40 días sin comprar es normal para alguien que compra cada 45 y es una alarma para alguien que compra cada 10 |
| `gasto_ultimo_mes` | Gasto de diciembre de 2025 | El comportamiento más reciente |
| `promedio_mensual_historico` | `AVG(gasto_mes) OVER (PARTITION BY usuario_id ...)` de los meses anteriores | La línea de base de cada usuario |
| **`trend_gasto`** (Trend) | `gasto_ultimo_mes - promedio_mensual_historico` | Capta el enfriamiento antes de que el cliente deje de comprar: un trend negativo indica que gasta menos que de costumbre |
| `r_score`, `f_score`, `m_score` | `NTILE(5) OVER (...)` sobre R, F y M | Segmentación RFM clásica en quintiles (5 = mejor). Son fáciles de interpretar para negocio y robustas a valores extremos |

## Lógica del script, paso a paso

La consulta principal es una cadena de CTEs que va de lo más crudo a lo más
agregado:

1. **`parametros`:** la fecha de corte y el último mes completo (diciembre).
2. **`pedidos_validos`:** solo los pedidos completados hasta el corte.
3. **`compras_con_gap`:** con **`LAG`** (función de ventana 1), cada compra obtiene
   los días desde la compra anterior del mismo usuario.

   ```sql
   date_diff('day',
             LAG(fecha_pedido) OVER (PARTITION BY usuario_id
                                     ORDER BY fecha_pedido, pedido_id),
             fecha_pedido) AS dias_desde_compra_anterior
   ```

4. **`resumen_rfm`:** `LEFT JOIN` desde `usuarios` y `GROUP BY usuario_id,
   fecha_registro`, que son todas las columnas no agregadas. De ahí salen R, F, M
   y el promedio de días entre compras.
5. **`meses_usuario` y `gasto_mensual`:** un calendario con un mes por usuario,
   desde **su mes de registro** hasta diciembre, y el gasto de cada mes (0 si no
   compró).
6. **`tendencia_mensual`:** con **`AVG ... OVER`** (función de ventana 2), el
   promedio de los meses **anteriores** a cada mes.

   ```sql
   AVG(gasto_mes) OVER (
       PARTITION BY usuario_id
       ORDER BY mes
       ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
   )
   ```

7. **Resultado final:** se unen las piezas, se resuelven los nulos y se agregan los
   scores con **`NTILE`** (función de ventana 3).

### Por qué el Trend se arma así (períodos que sesgan la métrica)

El promedio histórico se puede calcular mal de tres maneras:

| Forma incorrecta | Efecto | Cómo se evita |
|------------------|--------|---------------|
| Promediar solo los meses con compras (`GROUP BY` mes sin calendario) | Promedio inflado: los meses en 0 no cuentan y todos parecen enfriarse | El calendario `meses_usuario` con `LEFT JOIN` hace que cada mes sin compras exista y valga 0 |
| Contar meses anteriores al registro del usuario | Promedio desinflado: suma ceros de cuando el usuario todavía no existía | El calendario arranca en el mes de registro de cada usuario |
| Incluir el último mes en su propio promedio | El delta se achica hacia 0 | El marco `ROWS ... 1 PRECEDING` excluye la fila actual |

Además, el último mes es un mes **completo** (el corte es el 31/12). Si se
comparara un mes por la mitad contra meses completos, el trend saldría negativo
para todos por construcción.

### Manejo de nulos

El `LEFT JOIN` conserva a los 7 usuarios sin compras, que quedan con `NULL` en
todas las columnas de compras. Cada caso se resuelve con un valor que tiene
sentido:

| Situación | Valor asignado | Motivo |
|-----------|----------------|--------|
| `monetary`, `ticket_promedio` sin compras | `0` | No gastó nada |
| `recency_dias` sin compras | `antiguedad_dias` | Está inactivo desde que se registró |
| `dias_promedio_entre_compras` con 0 o 1 compra | Días desde la primera compra (o el registro) hasta el corte | No hay intervalo medible, pero el real es como mínimo ese |
| `promedio_mensual_historico` sin meses previos | `0` | No hay historial: todo lo que gastó cuenta como tendencia |
| `r/f/m_score` sin compras | `0` | Por debajo del peor cliente. Los quintiles se calculan solo entre clientes (`PARTITION BY tiene_compras`); si no, un usuario registrado hace poco y sin compras quedaría como "reciente" |

El control de calidad (consulta 2) confirma que el resultado tiene **60 filas, 60
usuarios distintos, la misma cantidad que el origen y 0 valores nulos**: los joins
no duplicaron ni perdieron a nadie.

## Validación: ¿las features predicen el churn?

Para comprobarlo se arma una etiqueta. Un cliente hace churn si no tiene ninguna
compra completada en los 59 días posteriores al corte (01/01 al 28/02/2026).

| churn | clientes | recency (días) | frequency | monetary | días entre compras | trend | r_score |
|------:|---------:|---------------:|----------:|---------:|-------------------:|------:|--------:|
| 0 (sigue) | 33 | 22,0 | 8,1 | 710,82 | 33,0 | +6,39 | 3,52 |
| 1 (abandona) | 20 | 123,3 | 4,9 | 343,21 | 55,0 | −17,36 | 2,00 |

Todas las features separan a los dos grupos en la dirección esperada: los que
abandonan llevan más tiempo sin comprar, compran menos, compran más espaciado y
vienen gastando menos que de costumbre. Por score de recency:

| r_score | clientes | tasa de churn |
|--------:|---------:|--------------:|
| 1 (más inactivos) | 11 | 90,9 % |
| 2 | 11 | 36,4 % |
| 3 | 11 | 27,3 % |
| 4 | 10 | 20,0 % |
| 5 (más recientes) | 10 | 10,0 % |

**Limitación del trend:** el trend es más ruidoso que la recency. Un cliente que
compra una vez por mes y justo no compró en diciembre muestra un trend negativo
aunque siga activo. Por eso conviene que el modelo lo combine con
`dias_promedio_entre_compras` y `recency_dias` y no lo use aislado. Con más datos,
una alternativa sería comparar trimestres en lugar de meses.

## Buenas prácticas aplicadas

- **Legibilidad:** CTEs con nombres descriptivos (`pedidos_validos`,
  `compras_con_gap`, `tendencia_mensual`), alias de tabla que se entienden (`ped`,
  `usr`, `rfm`, `tnd`) e indentación consistente. Cada función de ventana tiene un
  comentario que explica su `PARTITION BY`, su `ORDER BY` y su marco.
- **`GROUP BY` completo:** todas las columnas no agregadas del `SELECT` están en el
  `GROUP BY`.
- **Fecha de corte parametrizada:** está escrita una sola vez en la CTE
  `parametros`. Para recalcular las features a otra fecha alcanza con cambiarla ahí.
- **Tipos explícitos al cargar los CSV**, para que las fechas sean `DATE` y los
  montos `DECIMAL`.
- **Verificación cruzada:** recalculé `recency_dias`, `frequency`, `monetary` y
  `trend_gasto` en Python puro, por fuera del SQL, para los 60 usuarios, sin
  ninguna discrepancia.

## Checklist de la entrega

| Criterio | Dónde se cumple |
|----------|-----------------|
| Archivo `.sql` con la consulta principal funcional | [`features_churn.sql`](features_churn.sql), sección 1 (`CREATE TABLE features_churn AS ...`) |
| Al menos dos funciones de ventana | `LAG`, `AVG ... OVER (PARTITION BY ... ROWS ...)` y `NTILE` |
| Al menos tres métricas de comportamiento | Recency, Frequency, Monetary y Trend, además de ticket promedio, días entre compras y scores RFM |
| README con el objetivo de cada feature | Sección [Features generadas](#features-generadas) |
| Legibilidad (indentación y alias descriptivos) | Ver [Buenas prácticas aplicadas](#buenas-prácticas-aplicadas) |
| Nulos con valores coherentes | Sección [Manejo de nulos](#manejo-de-nulos) |
