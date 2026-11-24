-- 1. Dimensiones
CREATE TABLE IF NOT EXISTS dim_calendario (
    fecha DATE PRIMARY KEY,
    anio INT NOT NULL,
    mes INT NOT NULL,
    nombre_mes VARCHAR(15) NOT NULL,
    trimestre VARCHAR(2) NOT NULL,
    dia_semana_num INT NOT NULL,
    nombre_dia VARCHAR(15) NOT NULL,
    es_fin_de_semana BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_platillos (
    id_platillo INT PRIMARY KEY,
    nombre_platillo VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    precio_lista NUMERIC(10, 2) NOT NULL,
    costo_unitario NUMERIC(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_meseros (
    id_mesero INT PRIMARY KEY,
    nombre_mesero VARCHAR(100) NOT NULL,
    turno_base VARCHAR(20) NOT NULL,
    fecha_ingreso DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_metodos_pago (
    id_metodo_pago INT PRIMARY KEY,
    metodo_pago VARCHAR(50) NOT NULL,
    comision_pct NUMERIC(5, 4) NOT NULL
);

-- 2. Tabla de Hechos (Grano: 1 fila = 1 platillo vendido dentro de un ticket)
CREATE TABLE IF NOT EXISTS fact_ventas (
    id_venta INT PRIMARY KEY,
    id_ticket VARCHAR(20) NOT NULL,
    fecha DATE NOT NULL REFERENCES dim_calendario(fecha),
    hora TIME NOT NULL,
    id_platillo INT NOT NULL REFERENCES dim_platillos(id_platillo),
    id_mesero INT NOT NULL REFERENCES dim_meseros(id_mesero),
    id_metodo_pago INT NOT NULL REFERENCES dim_metodos_pago(id_metodo_pago),
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10, 2) NOT NULL,
    costo_unitario NUMERIC(10, 2) NOT NULL,
    descuento NUMERIC(10, 2) NOT NULL DEFAULT 0,
    propina NUMERIC(10, 2) NOT NULL DEFAULT 0,
    estatus VARCHAR(20) NOT NULL CHECK (estatus IN ('Completada', 'Cancelada'))
);

-- Índices para acelerar consultas analíticas
CREATE INDEX idx_fact_ventas_fecha ON fact_ventas(fecha);
CREATE INDEX idx_fact_ventas_platillo ON fact_ventas(id_platillo);
CREATE INDEX idx_fact_ventas_estatus ON fact_ventas(estatus);