"""Datos de ejemplo (inventados) de un restaurante-cafetería: inventario y consumo diario."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)

# producto, unidad, consumo diario promedio, costo unitario, stock actual, días de entrega, proveedor
ITEMS = [
    ("Café en grano", "kg", 6.0, 38000, 55, 3, "Cafés del Valle"),
    ("Leche entera", "L", 45.0, 3600, 130, 1, "Lácteos Andina"),
    ("Harina de trigo", "kg", 14.0, 3200, 520, 4, "Molinos SA"),
    ("Huevos (cubeta x30)", "cubeta", 5.0, 18500, 9, 2, "Granja Santa Ana"),
    ("Mantequilla", "kg", 3.5, 24000, 30, 3, "Lácteos Andina"),
    ("Azúcar", "kg", 9.0, 3800, 120, 4, "Molinos SA"),
    ("Aguacate", "kg", 12.0, 9500, 18, 1, "Frutas y Verduras Tolima"),
    ("Pollo (pechuga)", "kg", 16.0, 15500, 90, 2, "Avícola Central"),
    ("Pan de masa madre", "und", 60.0, 2800, 220, 1, "Panadería La Espiga"),
    ("Queso mozzarella", "kg", 7.0, 29000, 55, 3, "Lácteos Andina"),
    ("Tomate chonto", "kg", 13.0, 4200, 45, 1, "Frutas y Verduras Tolima"),
    ("Chocolate en barra", "kg", 2.5, 31000, 40, 5, "Cacao Real"),
    ("Aceite de oliva", "L", 3.0, 36000, 25, 6, "Importadora Medi"),
    ("Vasos 12 oz", "und", 150.0, 280, 2500, 7, "Empaques Bogotá"),
    ("Servilletas (paq x500)", "paq", 2.0, 8500, 6, 5, "Empaques Bogotá"),
]
cols = ["producto", "unidad", "consumo_diario_prom", "costo_unitario", "stock_actual", "dias_entrega", "proveedor"]
inv = pd.DataFrame(ITEMS, columns=cols)
inv.insert(0, "sku", [f"INV{i:03d}" for i in range(1, len(inv) + 1)])
inv.to_csv("inventario.csv", index=False)

# consumo diario de los últimos 60 días, con fines de semana más altos
dias = pd.date_range("2026-09-01", "2026-10-30", freq="D")
rows = []
for _, r in inv.iterrows():
    for d in dias:
        f = 1.25 if d.weekday() >= 4 else 0.9
        base = r.consumo_diario_prom * f
        c = max(0, rng.normal(base, base * 0.18))
        rows.append((d.date(), r.sku, round(float(c), 2)))
pd.DataFrame(rows, columns=["fecha", "sku", "consumo"]).to_csv("consumo_diario.csv", index=False)
print("inventario.csv y consumo_diario.csv generados")
