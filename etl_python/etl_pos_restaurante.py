import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Semilla fija para reproducibilidad
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/clean", exist_ok=True)


def crear_dimensiones():
    # 1. Dimensión Platillos (menú tipo restaurante casual / italiano)
    platillos = [
        (1, "Pasta Alfredo con Pollo", "Platos Fuertes", 215.00, 78.00),
        (2, "Lasaña Boloñesa", "Platos Fuertes", 235.00, 92.00),
        (3, "Pizza Pepperoni Artesanal", "Platos Fuertes", 220.00, 68.00),
        (4, "Pizza Margarita", "Platos Fuertes", 195.00, 56.00),
        (5, "Risotto de Hongos", "Platos Fuertes", 260.00, 110.00),
        (6, "Salmón a la Plancha", "Platos Fuertes", 310.00, 155.00),
        (7, "Ensalada César con Pollo", "Entradas", 165.00, 54.00),
        (8, "Pan de Ajo Gratinado", "Entradas", 95.00, 24.00),
        (9, "Dedos de Queso Mozzarella", "Entradas", 135.00, 45.00),
        (10, "Carpaccio de Res", "Entradas", 185.00, 82.00),
        (11, "Limonada Mineral", "Bebidas", 58.00, 11.00),
        (12, "Refresco de Lata", "Bebidas", 48.00, 14.00),
        (13, "Cerveza Artesanal", "Bebidas", 95.00, 32.00),
        (14, "Copa de Vino Tinto", "Bebidas", 145.00, 46.00),
        (15, "Café Americano", "Bebidas", 55.00, 9.00),
        (16, "Tiramisú Clásico", "Postres", 125.00, 38.00),
        (17, "Cheesecake de Frutos Rojos", "Postres", 118.00, 36.00),
        (18, "Brownie con Helado", "Postres", 110.00, 31.00),
    ]
    dim_platillos = pd.DataFrame(
        platillos,
        columns=["id_platillo", "nombre_platillo", "categoria", "precio_lista", "costo_unitario"],
    )

    # 2. Dimensión Meseros
    meseros = [
        (1, "Carlos Mendoza", "Vespertino", "2023-03-15"),
        (2, "Sofía Ramírez", "Vespertino", "2023-08-01"),
        (3, "Luis Torres", "Matutino", "2024-01-10"),
        (4, "Valeria Castro", "Vespertino", "2024-05-20"),
        (5, "Jorge Félix", "Matutino", "2024-09-01"),
        (6, "Andrea López", "Mixto", "2025-02-12"),
    ]
    dim_meseros = pd.DataFrame(
        meseros, columns=["id_mesero", "nombre_mesero", "turno_base", "fecha_ingreso"]
    )

    # 3. Dimensión Métodos de Pago
    metodos = [
        (1, "Efectivo", 0.0000),
        (2, "Tarjeta Débito", 0.0180),
        (3, "Tarjeta Crédito", 0.0290),
        (4, "Transferencia", 0.0000),
    ]
    dim_metodos_pago = pd.DataFrame(
        metodos, columns=["id_metodo_pago", "metodo_pago", "comision_pct"]
    )

    # 4. Dimensión Calendario (2025-01-01 a 2026-12-31)
    fechas = pd.date_range(start="2025-01-01", end="2026-12-31", freq="D")
    meses_es = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
    }
    dias_es = {
        0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
        4: "Viernes", 5: "Sábado", 6: "Domingo",
    }
    dim_calendario = pd.DataFrame({
        "fecha": fechas.strftime("%Y-%m-%d"),
        "anio": fechas.year,
        "mes": fechas.month,
        "nombre_mes": fechas.month.map(meses_es),
        "trimestre": "Q" + fechas.quarter.astype(str),
        "dia_semana_num": fechas.dayofweek + 1,  # 1=Lunes ... 7=Domingo
        "nombre_dia": fechas.dayofweek.map(dias_es),
        "es_fin_de_semana": fechas.dayofweek >= 4,  # Vie, Sáb, Dom
    })

    return dim_platillos, dim_meseros, dim_metodos_pago, dim_calendario


def generar_ventas_crudas(dim_platillos):
    """Simula tickets POS con patrones realistas e inyecta errores para demostrar ETL."""
    fechas = pd.date_range(start="2025-01-01", end="2026-11-22", freq="D")
    pesos_platillos = [
        0.10, 0.07, 0.11, 0.06, 0.03, 0.03,  # Platos Fuertes
        0.06, 0.07, 0.05, 0.02,              # Entradas
        0.11, 0.09, 0.06, 0.04, 0.04,        # Bebidas
        0.02, 0.02, 0.02                     # Postres
    ]
    horas_posibles = list(range(12, 23))  # 12:00 a 22:59
    pesos_horas = [0.04, 0.08, 0.12, 0.11, 0.06, 0.05, 0.08, 0.14, 0.16, 0.11, 0.05]

    registros = []
    ticket_counter = 100001
    venta_id = 1

    platillos_dict = dim_platillos.set_index("id_platillo").to_dict("index")

    for fecha in fechas:
        dia_sem = fecha.dayofweek  # 0=Lun, 6=Dom
        # Más tráfico fines de semana y crecimiento ~12% en 2026
        base_tickets = 14 if dia_sem < 4 else (24 if dia_sem == 4 else 28)
        if fecha.month in (5, 11, 12):  # Temporada alta (mayo, nov, dic)
            base_tickets = int(base_tickets * 1.18)
        if fecha.year == 2026:
            base_tickets = int(base_tickets * 1.12)

        num_tickets = max(6, int(np.random.normal(base_tickets, 3)))

        for _ in range(num_tickets):
            id_ticket = f"TKT-{ticket_counter}"
            ticket_counter += 1

            hora_h = random.choices(horas_posibles, weights=pesos_horas, k=1)[0]
            hora_m = random.randint(0, 59)
            hora_str = f"{hora_h:02d}:{hora_m:02d}:00"

            # Mesero según turno
            id_mesero = random.choice([3, 5, 6]) if hora_h < 17 else random.choice([1, 2, 4, 6])
            id_metodo_pago = random.choices([1, 2, 3, 4], weights=[0.28, 0.36, 0.28, 0.08], k=1)[0]

            # Mayor probabilidad de cancelación en horas pico nocturnas (19h-21h)
            prob_cancelacion = 0.075 if (hora_h in (19, 20, 21) and dia_sem >= 4) else 0.025
            estatus = "Cancelada" if random.random() < prob_cancelacion else "Completada"

            num_items = random.choices([1, 2, 3, 4, 5], weights=[0.12, 0.34, 0.30, 0.16, 0.08], k=1)[0]
            items_elegidos = random.choices(dim_platillos["id_platillo"].tolist(), weights=pesos_platillos, k=num_items)

            # Propina sobre el ticket completo (0 si está cancelada)
            pct_propina = 0.0 if estatus == "Cancelada" else random.choices([0.0, 0.10, 0.12, 0.15], weights=[0.15, 0.45, 0.25, 0.15], k=1)[0]

            for id_plat in items_elegidos:
                info = platillos_dict[id_plat]
                cantidad = random.choices([1, 2, 3], weights=[0.80, 0.16, 0.04], k=1)[0]
                precio = info["precio_lista"]
                costo = info["costo_unitario"]

                # Descuento ocasional (ej. promociones entre semana)
                descuento = round(precio * cantidad * 0.10, 2) if (dia_sem < 3 and random.random() < 0.12) else 0.00
                subtotal_neto = (precio * cantidad) - descuento
                propina_item = round(subtotal_neto * pct_propina, 2)

                registros.append({
                    "id_venta": venta_id,
                    "id_ticket": id_ticket,
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "hora": hora_str,
                    "id_platillo": id_plat,
                    "id_mesero": id_mesero,
                    "id_metodo_pago": id_metodo_pago,
                    "cantidad": cantidad,
                    "precio_unitario": precio,
                    "costo_unitario": costo,
                    "descuento": descuento,
                    "propina": propina_item,
                    "estatus": estatus,
                })
                venta_id += 1

    df_raw = pd.DataFrame(registros)

    # --- INYECCIÓN CONTROLADA DE ERRORES (DATOS SUCIOS PARA ETL) ---
    n = len(df_raw)
    # 1. Espacios y mayúsculas/minúsculas inconsistentes en estatus (3%)
    idx_estatus = df_raw.sample(frac=0.03, random_state=SEED).index
    df_raw.loc[idx_estatus, "estatus"] = df_raw.loc[idx_estatus, "estatus"].apply(
        lambda x: f" {x.upper()} " if random.random() < 0.5 else x.lower()
    )

    # 2. Precios unitarios nulos por fallo de sincronización POS (1%)
    idx_precio = df_raw.sample(frac=0.01, random_state=SEED + 1).index
    df_raw.loc[idx_precio, "precio_unitario"] = np.nan

    # 3. Método de pago nulo (0.8%)
    idx_pago = df_raw.sample(frac=0.008, random_state=SEED + 2).index
    df_raw.loc[idx_pago, "id_metodo_pago"] = np.nan

    # 4. Formato de fecha alternativo YYYY/MM/DD en 2% de filas
    idx_fecha = df_raw.sample(frac=0.02, random_state=SEED + 3).index
    df_raw.loc[idx_fecha, "fecha"] = df_raw.loc[idx_fecha, "fecha"].str.replace("-", "/")

    # 5. Filas duplicadas (1.5%)
    duplicados = df_raw.sample(frac=0.015, random_state=SEED + 4)
    df_raw = pd.concat([df_raw, duplicados], ignore_index=True)

    df_raw.to_csv("data/raw/raw_ventas_pos.csv", index=False)
    print(f"[RAW] Generado raw_ventas_pos.csv con {len(df_raw):,} registros (incluye errores controlados).")
    return df_raw


def limpiar_y_transformar(df_raw, dim_platillos):
    """Ejecuta limpieza ETL y genera reporte de calidad de datos."""
    df = df_raw.copy()
    filas_iniciales = len(df)

    # 1. Eliminar duplicados exactos
    df = df.drop_duplicates()
    duplicados_eliminados = filas_iniciales - len(df)

    # 2. Normalizar formato de fechas a YYYY-MM-DD
    df["fecha"] = pd.to_datetime(df["fecha"].str.replace("/", "-"), format="%Y-%m-%d").dt.strftime("%Y-%m-%d")

    # 3. Normalizar texto en estatus
    df["estatus"] = df["estatus"].astype(str).str.strip().str.title()

    # 4. Imputar precios unitarios nulos desde el catálogo oficial (dim_platillos)
    nulos_precio = df["precio_unitario"].isna().sum()
    mapa_precios = dim_platillos.set_index("id_platillo")["precio_lista"]
    df["precio_unitario"] = df["precio_unitario"].fillna(df["id_platillo"].map(mapa_precios))

    # 5. Imputar método de pago nulo con Efectivo (id=1, caso más común en fallos de captura)
    nulos_pago = df["id_metodo_pago"].isna().sum()
    df["id_metodo_pago"] = df["id_metodo_pago"].fillna(1).astype(int)

    # 6. Asegurar tipos de datos exactos para PostgreSQL
    df["id_venta"] = range(1, len(df) + 1)
    df["cantidad"] = df["cantidad"].astype(int)
    df["precio_unitario"] = df["precio_unitario"].round(2)
    df["costo_unitario"] = df["costo_unitario"].round(2)
    df["descuento"] = df["descuento"].round(2)
    df["propina"] = df["propina"].round(2)

    print("\n--- REPORTE DE CALIDAD ETL ---")
    print(f"Registros crudos:          {filas_iniciales:,}")
    print(f"Duplicados eliminados:     {duplicados_eliminados:,}")
    print(f"Precios nulos imputados:   {nulos_precio:,}")
    print(f"Pagos nulos imputados:     {nulos_pago:,}")
    print(f"Registros limpios finales: {len(df):,}")

    return df


if __name__ == "__main__":
    dim_platillos, dim_meseros, dim_metodos_pago, dim_calendario = crear_dimensiones()
    df_raw = generar_ventas_crudas(dim_platillos)
    fact_ventas = limpiar_y_transformar(df_raw, dim_platillos)

    # Exportar tablas limpias listas para cargar en PostgreSQL / Supabase
    dim_calendario.to_csv("data/clean/dim_calendario.csv", index=False)
    dim_platillos.to_csv("data/clean/dim_platillos.csv", index=False)
    dim_meseros.to_csv("data/clean/dim_meseros.csv", index=False)
    dim_metodos_pago.to_csv("data/clean/dim_metodos_pago.csv", index=False)
    fact_ventas.to_csv("data/clean/fact_ventas.csv", index=False)

    print("\n[OK] Archivos limpios guardados en data/clean/.")