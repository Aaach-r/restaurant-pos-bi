-- 1. Evolución mensual con crecimiento MoM% (Month-over-Month) usando CTE + LAG()
CREATE OR REPLACE VIEW vw_resumen_mensual AS
WITH ventas_mes AS (
    SELECT
        c.anio,
        c.mes,
        c.nombre_mes,
        COUNT(DISTINCT f.id_ticket) AS total_tickets,
        SUM((f.precio_unitario * f.cantidad) - f.descuento) AS ventas_netas,
        SUM(f.costo_unitario * f.cantidad) AS costo_total,
        SUM(((f.precio_unitario * f.cantidad) - f.descuento) - (f.costo_unitario * f.cantidad)) AS utilidad_bruta
    FROM fact_ventas f
    JOIN dim_calendario c ON f.fecha = c.fecha
    WHERE f.estatus = 'Completada'
    GROUP BY c.anio, c.mes, c.nombre_mes
)
SELECT
    anio,
    mes,
    nombre_mes,
    total_tickets,
    ROUND(ventas_netas, 2) AS ventas_netas,
    ROUND(utilidad_bruta, 2) AS utilidad_bruta,
    ROUND((utilidad_bruta / NULLIF(ventas_netas, 0)) * 100, 2) AS margen_bruto_pct,
    ROUND(ventas_netas / NULLIF(total_tickets, 0), 2) AS ticket_promedio,
    ROUND(
        ((ventas_netas - LAG(ventas_netas) OVER (ORDER BY anio, mes))
        / NULLIF(LAG(ventas_netas) OVER (ORDER BY anio, mes), 0)) * 100,
    2) AS crecimiento_mom_pct
FROM ventas_mes
ORDER BY anio, mes;


-- 2. Ingeniería de Menú (Popularidad vs Rentabilidad) usando funciones de ventana
CREATE OR REPLACE VIEW vw_ingenieria_menu AS
WITH metricas_platillo AS (
    SELECT
        p.id_platillo,
        p.nombre_platillo,
        p.categoria,
        SUM(f.cantidad) AS unidades_vendidas,
        SUM((f.precio_unitario * f.cantidad) - f.descuento) AS ventas_netas,
        SUM(((f.precio_unitario * f.cantidad) - f.descuento) - (f.costo_unitario * f.cantidad)) AS utilidad_bruta
    FROM fact_ventas f
    JOIN dim_platillos p ON f.id_platillo = p.id_platillo
    WHERE f.estatus = 'Completada'
    GROUP BY p.id_platillo, p.nombre_platillo, p.categoria
),
promedios AS (
    SELECT
        *,
        ROUND((utilidad_bruta / NULLIF(ventas_netas, 0)) * 100, 2) AS margen_pct,
        AVG(unidades_vendidas) OVER () AS prom_unidades,
        AVG((utilidad_bruta / NULLIF(ventas_netas, 0)) * 100) OVER () AS prom_margen
    FROM metricas_platillo
)
SELECT
    nombre_platillo,
    categoria,
    unidades_vendidas,
    ROUND(ventas_netas, 2) AS ventas_netas,
    ROUND(utilidad_bruta, 2) AS utilidad_bruta,
    margen_pct,
    CASE
        WHEN unidades_vendidas >= prom_unidades AND margen_pct >= prom_margen THEN 'Estrella'
        WHEN unidades_vendidas >= prom_unidades AND margen_pct < prom_margen  THEN 'Caballo de Batalla'
        WHEN unidades_vendidas < prom_unidades  AND margen_pct >= prom_margen THEN 'Rompecabezas'
        ELSE 'Perro'
    END AS clasificacion_menu
FROM promedios
ORDER BY utilidad_bruta DESC;


-- 3. Operación por Día y Hora Pico (incluye tasa de cancelación)
CREATE OR REPLACE VIEW vw_operacion_horas_pico AS
SELECT
    c.dia_semana_num,
    c.nombre_dia,
    EXTRACT(HOUR FROM f.hora)::INT AS hora_dia,
    COUNT(DISTINCT f.id_ticket) AS tickets_totales,
    COUNT(DISTINCT CASE WHEN f.estatus = 'Cancelada' THEN f.id_ticket END) AS tickets_cancelados,
    ROUND(
        (COUNT(DISTINCT CASE WHEN f.estatus = 'Cancelada' THEN f.id_ticket END)::NUMERIC
        / NULLIF(COUNT(DISTINCT f.id_ticket), 0)) * 100,
    2) AS tasa_cancelacion_pct,
    ROUND(SUM(CASE WHEN f.estatus = 'Completada' THEN (f.precio_unitario * f.cantidad) - f.descuento ELSE 0 END), 2) AS ventas_completadas
FROM fact_ventas f
JOIN dim_calendario c ON f.fecha = c.fecha
GROUP BY c.dia_semana_num, c.nombre_dia, EXTRACT(HOUR FROM f.hora)
ORDER BY c.dia_semana_num, hora_dia;