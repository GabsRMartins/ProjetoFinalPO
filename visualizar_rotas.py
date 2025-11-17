import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D


# ============================================================
# GERA COORDENADAS DAS CIDADES (SIMULADO)
# ============================================================
def gerar_coordenadas_cidades(n):
    np.random.seed(42)
    x = np.random.uniform(0, 100, n)
    y = np.random.uniform(0, 100, n)
    return np.vstack([x, y]).T


# ============================================================
# CARREGAR SOLUÇÃO
# ============================================================
with open("solution_summary.json", "r") as f:
    sol = json.load(f)

routes = sol["routes"]
used_presses = sol["used_presses"]

print("Prensas usadas:", used_presses)
print("Rotas carregadas com sucesso!\n")


# ============================================================
# Preparar coordenadas
# ============================================================
# Determinar número correto de cidades baseado nos dados
max_city = 0
for bloco in routes:
    for (j, k) in bloco["arcos"]:
        max_city = max(max_city, j, k)
n = max(50, max_city + 1)  # mínimo 50, ou o máximo encontrado

coords = gerar_coordenadas_cidades(n)
deposito = 0

# Paleta de cores HSV para melhor separação visual
cmap = plt.colormaps["hsv"]


# ============================================================
# INICIAR FIGURA COM SUBPLOTS (UMA POR PRENSA + GERAL)
# ============================================================
# Calcular número de subplots necessários
num_prensas = len(used_presses)
num_subplots = num_prensas + 1  # +1 para visão geral

# Layout: 1 linha para geral, restante para prensas (2 colunas)
num_rows = 1 + (num_prensas + 1) // 2  # +1 para a linha de texto
fig = plt.figure(figsize=(20, 5 * num_rows))

# Subplot 0: Visão geral (primeira linha, 2 colunas)
ax_geral = plt.subplot2grid((num_rows, 2), (0, 0), colspan=2, rowspan=1)
ax_geral.set_title("Visão Geral - Todas as Rotas", fontsize=14, weight="bold")

# Plotar cidades na visão geral
ax_geral.scatter(coords[:, 0], coords[:, 1], c="black", s=50, alpha=0.4, zorder=2)
for cid, (x, y) in enumerate(coords):
    ax_geral.text(x + 1, y + 1, str(cid), fontsize=6, alpha=0.5)

# Depósito em destaque
dx, dy = coords[deposito]
ax_geral.scatter([dx], [dy], c="red", s=300, marker="s", zorder=5)
ax_geral.text(dx + 2, dy + 2, "DEP", fontsize=10, color="red", weight="bold")

ax_geral.grid(True, linestyle="--", alpha=0.2)
ax_geral.set_xlabel("Coordenada X")
ax_geral.set_ylabel("Coordenada Y")


# ============================================================
# DESENHAR ROTAS
# ============================================================
for idx, bloco in enumerate(routes):
    i = bloco["pressa"]
    arcos = bloco["arcos"]

    if len(arcos) == 0:
        continue

    print(f"Prensa {i}: {len(arcos)} arcos")

    # Cor baseada no índice da prensa
    cor_idx = list(used_presses).index(i) / max(len(used_presses), 1)
    cor = cmap(cor_idx)
    
    # Subplot individual para cada prensa
    prensa_row = 1 + (idx // 2)
    if prensa_row < num_rows - 1:  # Deixar espaço para texto
        ax_prensa = plt.subplot2grid((num_rows, 2), (prensa_row, idx % 2), rowspan=1)
        ax_prensa.set_title(f"Rota Prensa {i}", fontsize=12, weight="bold", color=cor)
        
        # Plotar todas as cidades em cinza
        ax_prensa.scatter(coords[:, 0], coords[:, 1], c="lightgray", s=40, alpha=0.3, zorder=1)
        
        # Depósito
        ax_prensa.scatter([dx], [dy], c="red", s=250, marker="s", zorder=5)
        ax_prensa.text(dx + 2, dy + 2, "DEP", fontsize=10, color="red", weight="bold")
        
        ax_prensa.grid(True, linestyle="--", alpha=0.2)
        ax_prensa.set_xlabel("Coordenada X")
        ax_prensa.set_ylabel("Coordenada Y")

    # --------------------------------------------------------
    # RECONSTRUIR ROTAS A PARTIR DO DEPÓSITO - VERSÃO CORRIGIDA
    # --------------------------------------------------------
    # Construir dicionário de adjacência
    grafo = {}
    for (a, b) in arcos:
        if a not in grafo:
            grafo[a] = []
        grafo[a].append(b)
    
    # Reconstruir rota começando do depósito
    rota = []
    if deposito in grafo:
        atual = deposito
        visitados = set()
        
        while atual not in visitados and len(visitados) < len(arcos) + 2:
            visitados.add(atual)
            rota.append(atual)
            
            # Próximo nó
            if atual in grafo and len(grafo[atual]) > 0:
                atual = grafo[atual][0]  # pega primeiro destino
            else:
                break
    
    print(f"Prensa {i} - Rota reconstruída: {rota}")
    print(f"Prensa {i} - Arcos originais: {arcos}\n")

    # --------------------------------------------------------
    # DESENHAR ROTAS EM AMBOS OS SUBPLOTS
    # --------------------------------------------------------
    if len(rota) > 1:  # apenas desenha se tem rota válida
        for u, v in zip(rota[:-1], rota[1:]):
            if u != v:
                # Visão geral (com menor opacidade)
                arrow_geral = FancyArrowPatch(
                    coords[u], coords[v],
                    arrowstyle='-|>',
                    mutation_scale=8,
                    color=cor,
                    linewidth=1.2,
                    alpha=0.4,
                    connectionstyle="arc3,rad=0.1",
                    zorder=3
                )
                ax_geral.add_patch(arrow_geral)
                
                # Subplot individual (com maior destaque)
                if prensa_row < num_rows - 1:
                    arrow_prensa = FancyArrowPatch(
                        coords[u], coords[v],
                        arrowstyle='-|>',
                        mutation_scale=15,
                        color=cor,
                        linewidth=2.2,
                        alpha=0.75,
                        connectionstyle="arc3,rad=0.12",
                        zorder=4
                    )
                    ax_prensa.add_patch(arrow_prensa)
                    
                    # Destacar cidades visitadas
                    ax_prensa.scatter([coords[u, 0], coords[v, 0]], 
                                     [coords[u, 1], coords[v, 1]], 
                                     c=[cor], s=70, alpha=0.7, zorder=3)


# ============================================================
# LEGENDAS
# ============================================================
legend_elements = [
    Line2D([0], [0], marker='o', markersize=8, color='black', label="Cidade"),
    Line2D([0], [0], marker='s', markersize=12, color='red', label="Depósito"),
]

for idx, pid in enumerate(used_presses):
    cor_idx = idx / max(len(used_presses), 1)
    cor = cmap(cor_idx)
    legend_elements.append(
        Line2D([0], [0], color=cor, lw=3, label=f"Prensa {pid}")
    )

ax_geral.legend(handles=legend_elements, fontsize=11, loc="upper left", framealpha=0.95)

# ============================================================
# ADICIONAR TEXTO DAS ROTAS EM UM SUBPLOT SEPARADO
# ============================================================
# Coletar todas as rotas em texto
rotas_info = []
for idx, bloco in enumerate(routes):
    i = bloco["pressa"]
    arcos = bloco["arcos"]
    
    if len(arcos) == 0:
        continue
    
    # Reconstruir rotas
    grafo = {}
    for (a, b) in arcos:
        if a not in grafo:
            grafo[a] = []
        grafo[a].append(b)
    
    # Reconstruir rota
    rota = []
    if deposito in grafo:
        atual = deposito
        visitados = set()
        
        while atual not in visitados and len(visitados) < len(arcos) + 2:
            visitados.add(atual)
            rota.append(atual)
            if atual in grafo and len(grafo[atual]) > 0:
                atual = grafo[atual][0]
            else:
                break
    
    # Formatar texto da rota
    rota_str = " → ".join(map(str, rota))
    rotas_info.append(f"Prensa {i}:\n  {rota_str}\n")

# Criar subplot para mostrar todas as rotas
ax_texto = plt.subplot2grid((num_rows, 2), (num_rows - 1, 0), colspan=2)
ax_texto.axis('off')
ax_texto.set_ylim(0, 1)
texto_completo = "".join(rotas_info)
ax_texto.text(0.02, 0.98, texto_completo, 
             transform=ax_texto.transAxes,
             fontsize=9, verticalalignment='top', family='monospace',
             wrap=True,
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.85, pad=1))

plt.suptitle(f"VRP com {len(used_presses)} Prensa(s) | Valor Objetivo: {sol['objective']:.2f}", 
             fontsize=16, weight="bold", y=0.995)
plt.tight_layout()
plt.show()

