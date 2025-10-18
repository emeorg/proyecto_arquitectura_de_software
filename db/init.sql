/*
 * =================================================================
 * SCRIPT DE EJEMPLO (REALISTA) - PRODUCTOS (CLP)
 * =================================================================
 *
 * Propósito:
 * Demostración de una tabla de productos con precios en
 * Pesos Chilenos (CLP), usando el tipo de dato correcto (Entero).
 */

-- Crear la tabla 'productos'
CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    -- Usamos NUMERIC para CLP, ya que no tiene decimales
    precio NUMERIC(10, 0) NOT NULL CHECK (precio >= 0)
);

-- Insertar datos de ejemplo con precios reales en CLP
INSERT INTO productos (nombre, precio) VALUES
    ('Café en Grano (1kg)', 12990),
    ('Teclado Mecánico', 79990),
    ('Mouse Inalámbrico', 24990),
    ('Monitor 24 pulgadas', 159990),
    ('Auriculares Bluetooth', 49990),
    ('Disco Duro Externo 1TB', 69990),
    ('Smartphone Gama Media', 199990),
    ('Tablet 10 pulgadas', 149990),
    ('Impresora Multifuncional', 89990),
    ('Router WiFi 6', 119990);