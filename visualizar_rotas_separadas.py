import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D
import os
from datetime import datetime


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

# Criar diretório para gráficos separados
output_dir = "graficos_separados"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# ============================================================
# 1. GRÁFICO COMPLETO - VISÃO GERAL
# ============================================================
print("=" * 60)
print("Gerando gráfico completo...")
print("=" * 60)

fig_geral = plt.figure(figsize=(16, 10))
ax_geral = fig_geral.add_subplot(111)
ax_geral.set_title("Visão Geral - Todas as Rotas VRP", fontsize=16, weight="bold", pad=20)

# Plotar cidades
ax_geral.scatter(coords[:, 0], coords[:, 1], c="black", s=80, alpha=0.5, zorder=2, label="Cidades")

# Depósito em destaque
dx, dy = coords[deposito]
ax_geral.scatter([dx], [dy], c="red", s=400, marker="s", zorder=5, label="Depósito", edgecolors="darkred", linewidth=2)
ax_geral.text(dx + 2, dy + 2, "DEPÓSITO", fontsize=11, color="red", weight="bold", bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

# Desenhar todas as rotas
for idx, bloco in enumerate(routes):
    i = bloco["pressa"]
    arcos = bloco["arcos"]

    if len(arcos) == 0:
        continue

    # Cor baseada no índice da prensa
    cor_idx = list(used_presses).index(i) / max(len(used_presses), 1)
    cor = cmap(cor_idx)
    
    # Construir dicionário de adjacência
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
    
    # Desenhar rotas
    if len(rota) > 1:
        for u, v in zip(rota[:-1], rota[1:]):
            if u != v:
                arrow = FancyArrowPatch(
                    coords[u], coords[v],
                    arrowstyle='-|>',
                    mutation_scale=10,
                    color=cor,
                    linewidth=1.5,
                    alpha=0.6,
                    connectionstyle="arc3,rad=0.15",
                    zorder=3
                )
                ax_geral.add_patch(arrow)
        
        # Desenhar último arco voltando para o depósito
        if len(rota) > 1 and rota[-1] != deposito:
            arrow_volta = FancyArrowPatch(
                coords[rota[-1]], coords[deposito],
                arrowstyle='-|>',
                mutation_scale=10,
                color=cor,
                linewidth=1.5,
                alpha=0.6,
                connectionstyle="arc3,rad=0.15",
                linestyle='--',
                zorder=3
            )
            ax_geral.add_patch(arrow_volta)
    
    # Adicionar números das cidades no gráfico completo
    for idx_cidade, (x, y) in enumerate(coords):
        if idx_cidade != deposito:  # Não adiciona número no depósito
            ax_geral.text(x, y - 2.5, str(idx_cidade), fontsize=8, weight='bold', 
                         ha='center', bbox=dict(boxstyle='circle,pad=0.2', facecolor='white', alpha=0.8))

# Legendas
legend_elements = [
    Line2D([0], [0], marker='o', markersize=10, color='black', linestyle='none', label="Cidades"),
    Line2D([0], [0], marker='s', markersize=12, color='red', linestyle='none', label="Depósito"),
]

for idx, pid in enumerate(used_presses):
    cor_idx = idx / max(len(used_presses), 1)
    cor = cmap(cor_idx)
    legend_elements.append(
        Line2D([0], [0], color=cor, lw=3, label=f"Prensa {pid}")
    )

ax_geral.legend(handles=legend_elements, fontsize=11, loc="upper left", framealpha=0.95, ncol=2)
ax_geral.grid(True, linestyle="--", alpha=0.2)
ax_geral.set_xlabel("Coordenada X", fontsize=12)
ax_geral.set_ylabel("Coordenada Y", fontsize=12)

plt.suptitle(f"VRP Completo com {len(used_presses)} Prensa(s) | Valor Objetivo: {sol['objective']:.2f}", 
             fontsize=14, weight="bold", y=0.98)
plt.tight_layout()

# Salvar gráfico completo
output_file = os.path.join(output_dir, "00_grafico_completo.png")
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✓ Gráfico completo salvo em: {output_file}")
plt.close()


# ============================================================
# 2. GRÁFICOS INDIVIDUAIS PARA CADA PRENSA
# ============================================================
print("\n" + "=" * 60)
print("Gerando gráficos individuais para cada prensa...")
print("=" * 60)

for idx, bloco in enumerate(routes):
    i = bloco["pressa"]
    arcos = bloco["arcos"]

    if len(arcos) == 0:
        print(f"⚠ Prensa {i}: sem rotas (arcos vazio)")
        continue

    print(f"Prensa {i}: {len(arcos)} arcos")

    # Cor baseada no índice da prensa
    cor_idx = list(used_presses).index(i) / max(len(used_presses), 1)
    cor = cmap(cor_idx)
    
    # Criar figura para prensa individual
    fig_prensa = plt.figure(figsize=(14, 10))
    
    # Subplot 1: Mapa da rota
    ax_mapa = plt.subplot(2, 1, 1)
    ax_mapa.set_title(f"Rota da Prensa {i}", fontsize=14, weight="bold", color=cor)
    
    # Plotar todas as cidades em cinza claro
    ax_mapa.scatter(coords[:, 0], coords[:, 1], c="lightgray", s=100, alpha=0.3, zorder=1)
    
    # Depósito
    ax_mapa.scatter([dx], [dy], c="red", s=400, marker="s", zorder=5, edgecolors="darkred", linewidth=2)
    ax_mapa.text(dx + 2, dy + 2, "DEP", fontsize=10, color="red", weight="bold", 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    # Construir dicionário de adjacência
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
    
    print(f"  Rota reconstruída: {rota}")
    
    # Desenhar rotas
    if len(rota) > 1:
        for u, v in zip(rota[:-1], rota[1:]):
            if u != v:
                arrow = FancyArrowPatch(
                    coords[u], coords[v],
                    arrowstyle='-|>',
                    mutation_scale=18,
                    color=cor,
                    linewidth=2.5,
                    alpha=0.8,
                    connectionstyle="arc3,rad=0.15",
                    zorder=4
                )
                ax_mapa.add_patch(arrow)
                
                # Destacar cidades visitadas
                ax_mapa.scatter([coords[u, 0], coords[v, 0]], 
                               [coords[u, 1], coords[v, 1]], 
                               c=[cor], s=150, alpha=0.9, zorder=3, edgecolors='black', linewidth=1)
        
        # Desenhar último arco voltando para o depósito
        if len(rota) > 1 and rota[-1] != deposito:
            arrow_volta = FancyArrowPatch(
                coords[rota[-1]], coords[deposito],
                arrowstyle='-|>',
                mutation_scale=18,
                color=cor,
                linewidth=2.5,
                alpha=0.8,
                connectionstyle="arc3,rad=0.15",
                linestyle='--',
                zorder=4
            )
            ax_mapa.add_patch(arrow_volta)
    
    # Adicionar números das cidades no mapa da prensa individual
    for idx_cidade, (x, y) in enumerate(coords):
        if idx_cidade != deposito:  # Não adiciona número no depósito
            ax_mapa.text(x, y - 2.5, str(idx_cidade), fontsize=9, weight='bold', 
                        ha='center', bbox=dict(boxstyle='circle,pad=0.3', facecolor='white', alpha=0.9, edgecolor='black', linewidth=0.5))
    
    ax_mapa.grid(True, linestyle="--", alpha=0.2)
    ax_mapa.set_xlabel("Coordenada X", fontsize=11)
    ax_mapa.set_ylabel("Coordenada Y", fontsize=11)
    
    # Subplot 2: Informações da rota
    ax_info = plt.subplot(2, 1, 2)
    ax_info.axis('off')
    
    # Montar informações detalhadas
    info_text = f"""
INFORMAÇÕES DA PRENSA {i}

{'─' * 70}

Número de Arcos:        {len(arcos)}
Cidades Visitadas:      {len(rota) - 1} cidades (excluindo retorno ao depósito)

Rota Detalhada:
  {' → '.join(map(str, rota))}

Arcos (origem → destino):
"""
    
    for arc_idx, (a, b) in enumerate(arcos, 1):
        info_text += f"\n  {arc_idx:2d}. Cidade {a:2d} → Cidade {b:2d}"
    
    info_text += f"""

{'─' * 70}

Status:                 Ativa
Custo Total Estimado:   Vide modelo de otimização
Tempo Total:            Vide modelo de otimização
    """
    
    ax_info.text(0.05, 0.95, info_text, 
                transform=ax_info.transAxes,
                fontsize=10, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9, pad=1.5))
    
    # Legendas para cores
    legend_elements_prensa = [
        Line2D([0], [0], marker='o', markersize=10, color=cor, linestyle='none', 
               label=f"Cidades da Prensa {i}"),
        Line2D([0], [0], marker='s', markersize=12, color='red', linestyle='none', 
               label="Depósito"),
        Line2D([0], [0], color=cor, lw=3, label="Rota desta Prensa"),
    ]
    
    ax_mapa.legend(handles=legend_elements_prensa, fontsize=11, loc="upper right", framealpha=0.95)
    
    # Título geral
    plt.suptitle(f"Detalhes da Rota - Prensa {i}", fontsize=14, weight="bold", y=0.995)
    plt.tight_layout()
    
    # Salvar gráfico individual
    output_file = os.path.join(output_dir, f"{idx+1:02d}_prensa_{i}.png")
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Gráfico da Prensa {i} salvo em: {output_file}")
    plt.close()


# ============================================================
# 3. ARQUIVO DE RESUMO EM TEXTO
# ============================================================
print("\n" + "=" * 60)
print("Gerando arquivo de resumo...")
print("=" * 60)

resumo_text = f"""
{'=' * 80}
RESUMO DA SOLUÇÃO DO PROBLEMA DE ROTEAMENTO DE VEÍCULOS (VRP)
{'=' * 80}

Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Arquivo de Solução: solution_summary.json

{'─' * 80}
ESTATÍSTICAS GERAIS
{'─' * 80}

Número de Prensas Utilizadas:     {len(used_presses)}
Valor do Objetivo:                {sol['objective']:.2f}
Total de Rotas:                   {len(routes)}

Prensas Ativas:  {', '.join(map(str, sorted(used_presses)))}

{'─' * 80}
DETALHES POR PRENSA
{'─' * 80}
"""

for idx, bloco in enumerate(routes):
    i = bloco["pressa"]
    arcos = bloco["arcos"]
    
    if len(arcos) == 0:
        continue
    
    # Reconstruir rota
    grafo = {}
    for (a, b) in arcos:
        if a not in grafo:
            grafo[a] = []
        grafo[a].append(b)
    
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
    
    rota_str = " → ".join(map(str, rota))
    
    resumo_text += f"""
PRENSA {i}
  Arcos: {len(arcos)}
  Cidades Visitadas: {len(rota) - 1}
  Rota: {rota_str}
  Arquivo Gerado: {idx+1:02d}_prensa_{i}.png

"""

resumo_text += f"""
{'=' * 80}
ARQUIVOS GERADOS
{'=' * 80}

1. 00_grafico_completo.png       - Visão geral com todas as rotas
2. XX_prensa_N.png                - Gráfico individual para cada prensa com detalhes

Todos os arquivos estão no diretório: {output_dir}/

{'=' * 80}
"""

resumo_file = os.path.join(output_dir, "RESUMO.txt")
with open(resumo_file, 'w', encoding='utf-8') as f:
    f.write(resumo_text)

print(f"✓ Arquivo de resumo salvo em: {resumo_file}")


print("\n" + "=" * 60)
print("✓ PROCESSO CONCLUÍDO COM SUCESSO!")
print("=" * 60)
print(f"\nArquivos gerados em: {os.path.abspath(output_dir)}/")
print(f"  - 1 gráfico completo")
print(f"  - {len(routes)} gráficos individuais (um por prensa)")
print(f"  - 1 arquivo de resumo (RESUMO.txt)")
