# Análisis Comercial y Operativo — Restaurante POS (End-to-End BI)


Proyecto **end-to-end de Business Intelligence** diseñado para transformar datos transaccionales de un punto de venta (POS) restaurantero en decisiones comerciales y operativas accionables. Cubre todo el ciclo analítico: generación y limpieza ETL en **Python**, modelado dimensional en **PostgreSQL (Supabase)**, validación mediante **vistas SQL** y visualización ejecutiva interactiva en **Power BI**.

---

## Contexto y Problema de Negocio

En la operación diaria de un restaurante, el volumen de ventas bruto suele ocultar fugas clave de rentabilidad: platillos muy populares con márgenes bajos, comisiones bancarias que erosionan la utilidad, cuellos de botella en cocina durante horarios pico y tickets cancelados que impactan directamente en el ingreso neto.

Este proyecto responde cuatro preguntas centrales para dirección y gerencia operativa:
1. **Salud financiera:** ¿Cuánto vendemos realmente, cuál es el margen bruto real y cómo evolucionamos año contra año (YoY) y mes contra mes (MoM)?
2. **Ingeniería de menú:** ¿Qué platillos son *Estrellas* (alto volumen y alto margen) y cuáles requieren ajuste de precio, receta o empuje comercial?
3. **Saturación operativa:** ¿En qué días y franjas horarias se concentra la demanda y cuándo se disparan las cancelaciones?
4. **Desempeño del equipo:** ¿Cómo rinden los meseros por turno en ventas netas, ticket promedio, propinas y tasa de cancelación?

---

## Arquitectura del Proyecto

```text
Python (ETL & Limpieza) ──▶ CSVs Limpios ──▶ Supabase / PostgreSQL (Modelo Estrella + Vistas SQL) ──▶ Power BI (DAX + 3 Páginas)
