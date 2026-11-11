# Control de inventario con alertas de stock

Herramienta que le dice a un restaurante, cafetería o tienda **qué se le va a acabar antes de que
llegue el próximo pedido** y cuánto debe pedirle a cada proveedor.

## Qué resuelve

Se pierden ventas cuando se agota un insumo y se pierde dinero cuando se compra de más. Aquí cada
producto se evalúa con su consumo reciente y el tiempo que tarda su proveedor en entregar.

## Cómo calcula

| Concepto | Fórmula |
| --- | --- |
| Consumo reciente | Promedio de los últimos 14 días |
| Días de cobertura | stock actual ÷ consumo reciente |
| Punto de reorden | consumo × (días de entrega + 2 días de seguridad) |
| **Crítico** | cobertura ≤ días de entrega: se agota antes de que llegue un pedido |
| **Pedir ya** | stock ≤ punto de reorden |
| **Exceso** | más de 30 días de cobertura (capital inmovilizado) |
| Cantidad a pedir | consumo × (10 días + días de entrega) − stock actual |

Los parámetros (`COBERTURA_OBJETIVO`, `STOCK_SEGURIDAD`) están al inicio de `alertas.py`.

## Archivos

| Archivo | Descripción |
| --- | --- |
| `generate_data.py` | Crea `inventario.csv` y `consumo_diario.csv` (datos inventados) |
| `alertas.py` | Calcula alertas y genera `tablero.html`, `alertas.csv` y `pedido_sugerido.csv` |
| `dashboard_kit.py` | Diseño del tablero |

## Uso

```bash
pip install -r requirements.txt
python generate_data.py
python alertas.py
```

## Con datos reales

Reemplaza `inventario.csv` (sku, producto, unidad, costo_unitario, stock_actual, dias_entrega,
proveedor) y `consumo_diario.csv` (fecha, sku, consumo) y vuelve a ejecutar `alertas.py`.

## Tecnologías

Python, pandas, matplotlib, HTML/CSS.


## Qué busca (el problema)

Se pierden ventas por agotados y dinero por exceso de compra.

## Cómo se cumple

Calcula días de cobertura y punto de reorden según el consumo y el tiempo del proveedor; clasifica Crítico/Pedir ya/Exceso/OK y sugiere el pedido.

## Cómo ofrecerlo como servicio

- **Qué entrego:** Adaptación a tu catálogo, tablero y pedido sugerido por proveedor.
- **A quién:** Restaurantes, cafeterías, tiendas y ferreterías con inventario en Excel.
- **Precio de referencia (ajustar):** Implementación: 400.000–1.000.000 COP. Actualización semanal opcional: 150.000–300.000 COP.
- **Frase para empezar:** «Te aviso qué se te va a acabar antes de que llegue tu proveedor y cuánto pedir.»
- **Flujo:** 1) reunión corta y datos del cliente → 2) prototipo con sus datos → 3) ajustes → 4) entrega y capacitación.

> Datos del repositorio inventados; ejecutar los scripts para reproducir el tablero.
