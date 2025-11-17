import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
from matplotlib.collections import PatchCollection


# ============================================================
# Coordenadas simuladas (use suas reais se tiver futuramente)
# ============================================================
def gerar_coordenadas_cidades(n):
    np.random.seed(42)
    x = np.random.uniform(0, 100, n)
    y = np.random.uniform(0, 100, n)
    return np.vstack([x, y]).T


# ============================================================
# Desenha seta curva — muito mais bonito que arrow padrão
# ============================================================
def draw_curve_arrow(ax, start, end, color, lw=2, label=None):
    x1, y1 = start
    x2, y2 = end
    
    # Curvatura suave
    style = "arc3,rad=0.15"
    
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='-|>',
        mutation_scale=12,
        color=color,
        linewidth=lw,
        connectionstyle=style,
        alpha=0.9
    )
    ax.add_patch(arrow)


# ============================================================
# Carregar solução
# ============================================================
with open("solution_summary.json", "r") as f:
    sol = json.load(f)

routes = sol.get("routes", [])
used_presses = sol.get("used_presses", [])

print(f"Prensas usadas: {used_presses}")
print(f"Rotas encontradas: {len(routes)}")

# número de cidades
n = 50
coords = gerar_coordenadas_cidades(n)

# ============================================================
# Construir rotas por prensa a partir do novo formato
# ============================================================
rotas_por_prensa = {}
for bloco in routes:
    i = bloco["pressa"]
    arcos = bloco["arcos"]
    rotas_por_prensa[i] = arcos


# ============================================================
# Construir gráfico
# ============================================================
fig, ax = plt.subplots(figsize=(14, 11))
ax.set_title("Visualização das Rotas das Prensas", fontsize=16, pad=20)

# ------------------------------------------------------------
# Plot cidades
# ------------------------------------------------------------
ax.scatter(coords[:, 0], coords[:, 1], c="black", s=80, label="Cidades")

# Labels
for cid in range(n):
    x, y = coords[cid]
    ax.text(x+0.7, y+0.7, str(cid), fontsize=9, color="black")

# ------------------------------------------------------------
# Cores por prensa
# ------------------------------------------------------------
cores = plt.cm.get_cmap("tab20", 20)

# ------------------------------------------------------------
# Desenhar rotas por prensa (curvas)
# ------------------------------------------------------------
for i, rotas in rotas_por_prensa.items():
    cor = cores(i)

    # Ordenar rotas para formar caminho
    # Construir grafo j->k e percorrer
    grafo = {j: k for (j, k) in rotas}

    # Encontrar nós de início (que não aparecem como destino)
    destinos = {k for (_, k) in rotas}
    inicios = [j for (j, _) in rotas if j not in destinos]

    # Em teoria deve haver 1 início por rota simples
    for inicio in inicios:
        atual = inicio
        
        caminho = [atual]
        while atual in grafo:
            prox = grafo[atual]
            caminho.append(prox)
            atual = prox

        # Desenhar seta entre cidades no caminho
        for a, b in zip(caminho[:-1], caminho[1:]):
            coord_a = coords[a]
            coord_b = coords[b]
            draw_curve_arrow(ax, coord_a, coord_b, cor, lw=2.5)
            # marcador do ID da prensa
            xm = (coord_a[0] + coord_b[0]) / 2
            ym = (coord_a[1] + coord_b[1]) / 2
            ax.text(
                xm, ym, f"P{i}",
                fontsize=9, color=cor, weight="bold"
            )


# ------------------------------------------------------------
# Legenda customizada
# ------------------------------------------------------------
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='black', markersize=8, label='Cidade'),
]

for i in rotas_por_prensa.keys():
    legend_elements.append(
        Line2D([0], [0], color=cores(i), lw=3, label=f"Prensa {i}")
    )

ax.legend(handles=legend_elements, fontsize=10, loc='upper left')

# ------------------------------------------------------------
# Estética
# ------------------------------------------------------------
ax.grid(True, linestyle='--', alpha=0.4)
ax.set_xlabel("Coord X")
ax.set_ylabel("Coord Y")


plt.tight_layout()
plt.show()
