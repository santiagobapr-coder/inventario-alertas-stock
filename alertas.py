"""Inventario y alertas de stock -> tablero.html + alertas.csv + pedido_sugerido.csv"""
import matplotlib.pyplot as plt
import pandas as pd

from dashboard_kit import PALETTE, money, render_dashboard, table_html, tag

COBERTURA_OBJETIVO = 10  # días de stock que queremos tener tras recibir un pedido
STOCK_SEGURIDAD = 2      # días extra de colchón

inv = pd.read_csv("inventario.csv")
con = pd.read_csv("consumo_diario.csv", parse_dates=["fecha"])

# Consumo promedio de los últimos 14 días (refleja la demanda reciente)
rec = con[con.fecha > con.fecha.max() - pd.Timedelta(days=14)]
prom = rec.groupby("sku")["consumo"].mean().rename("consumo_14d")
inv = inv.merge(prom, on="sku")

inv["dias_cobertura"] = inv["stock_actual"] / inv["consumo_14d"]
inv["punto_reorden"] = inv["consumo_14d"] * (inv["dias_entrega"] + STOCK_SEGURIDAD)
inv["cantidad_pedir"] = (
    (inv["consumo_14d"] * (COBERTURA_OBJETIVO + inv["dias_entrega"]) - inv["stock_actual"])
    .clip(lower=0)
    .round(0)
)


def estado(r):
    if r.dias_cobertura <= r.dias_entrega:
        return "Crítico"
    if r.stock_actual <= r.punto_reorden:
        return "Pedir ya"
    if r.dias_cobertura > 30:
        return "Exceso"
    return "OK"


inv["estado"] = inv.apply(estado, axis=1)
# solo se sugiere pedido para lo que está en alerta
inv.loc[~inv["estado"].isin(["Crítico", "Pedir ya"]), "cantidad_pedir"] = 0
inv["valor_stock"] = inv["stock_actual"] * inv["costo_unitario"]
inv["costo_pedido"] = inv["cantidad_pedir"] * inv["costo_unitario"]

orden = {"Crítico": 0, "Pedir ya": 1, "OK": 2, "Exceso": 3}
inv = inv.sort_values(["estado", "dias_cobertura"], key=lambda s: s.map(orden) if s.name == "estado" else s)

alertas = inv[inv.estado.isin(["Crítico", "Pedir ya"])]
alertas[["sku", "producto", "proveedor", "stock_actual", "dias_cobertura", "dias_entrega", "estado"]].round(1).to_csv("alertas.csv", index=False)
ped = inv[inv.cantidad_pedir > 0][["proveedor", "sku", "producto", "unidad", "cantidad_pedir", "costo_pedido"]]
ped.sort_values(["proveedor", "producto"]).to_csv("pedido_sugerido.csv", index=False)

# --- Gráfico 1: días de cobertura vs. días de entrega
g = inv.sort_values("dias_cobertura")
colores = {"Crítico": PALETTE["bad"], "Pedir ya": PALETTE["warn"], "OK": PALETTE["good"], "Exceso": PALETTE["muted"]}
fig1, ax = plt.subplots(figsize=(7.4, 5.2))
ax.barh(g.producto, g.dias_cobertura, color=[colores[e] for e in g.estado])
ax.scatter(g.dias_entrega, g.producto, marker="|", s=260, color=PALETTE["ink"], zorder=3, label="Días de entrega del proveedor")
ax.set_xlabel("Días de cobertura (stock actual / consumo reciente)")
ax.set_title("¿Cuántos días me alcanza cada producto?")
ax.legend(frameon=False, loc="lower right")
ax.grid(axis="y", visible=False)

# --- Gráfico 2: consumo diario del producto crítico más importante
top = alertas.iloc[0]
serie = con[con.sku == top.sku].set_index("fecha")["consumo"]
fig2, ax = plt.subplots(figsize=(7.4, 3.4))
ax.plot(serie.index, serie.values, color=PALETTE["muted"], lw=1.2, label="Consumo diario")
ax.plot(serie.index, serie.rolling(7).mean(), color=PALETTE["primary"], lw=2.6, label="Promedio 7 días")
ax.set_title(f"Consumo de {top.producto} ({top.unidad}/día)")
ax.legend(frameon=False)
fig2.autofmt_xdate()

# --- Tabla de alertas
filas = []
for _, r in alertas.iterrows():
    kind = "bad" if r.estado == "Crítico" else "warn"
    filas.append([
        r.producto, r.proveedor, f"{r.stock_actual:,.0f} {r.unidad}", f"{r.dias_cobertura:.1f}",
        f"{r.dias_entrega}", f"{r.cantidad_pedir:,.0f} {r.unidad}", tag(r.estado, kind),
    ])
tabla = table_html(["Producto", "Proveedor", "Stock", "Días de cobertura", "Días de entrega", "Pedir", "Estado"], filas)

# --- Pedido por proveedor
res = ped.groupby("proveedor").agg(productos=("producto", "count"), total=("costo_pedido", "sum")).sort_values("total", ascending=False)
filas2 = [[p, str(int(r.productos)), money(r.total)] for p, r in res.iterrows()]
tabla2 = table_html(["Proveedor", "Productos a pedir", "Valor estimado"], filas2)

render_dashboard(
    "tablero.html",
    "Control de inventario · Alertas de reposición",
    "Cafetería-restaurante · Consumo de los últimos 14 días · Datos de ejemplo",
    kpis=[
        ("Productos en estado crítico", str((inv.estado == "Crítico").sum()), "no alcanzan para el plazo de entrega", "down"),
        ("Productos por pedir ya", str((inv.estado == "Pedir ya").sum()), "bajo el punto de reorden", ""),
        ("Valor del inventario", money(inv.valor_stock.sum())),
        ("Pedido sugerido total", money(inv.costo_pedido.sum()), f"{len(ped)} productos, cobertura de {COBERTURA_OBJETIVO} días"),
    ],
    sections=[
        {"title": "Cobertura por producto", "note": "Barra: días que alcanza el stock. Marca negra: días que demora el proveedor en entregar. Si la barra no llega a la marca, se agota antes de que llegue el pedido.", "figs": [fig1]},
        {"title": "Alertas de reposición", "note": "Crítico: se acaba antes de que llegue un pedido nuevo. Pedir ya: ya está bajo el punto de reorden (consumo × (entrega + 2 días de seguridad)).", "html": tabla},
        {"title": "Pedido sugerido por proveedor", "note": "Cantidad para volver a tener 10 días de cobertura después de la entrega. El detalle está en pedido_sugerido.csv.", "html": tabla2},
        {"title": "Tendencia de consumo", "note": "Se muestra el producto con la alerta más urgente.", "figs": [fig2]},
    ],
)
print(inv[["producto", "stock_actual", "dias_cobertura", "dias_entrega", "estado", "cantidad_pedir"]].round(1).to_string(index=False))
