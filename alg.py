# alg_fixed.py
"""
VRP de 1 viagem por prensa (cada prensa = 1 veículo)
v[j] é contínua (volume processado)
Objetivo: mantém a mesma forma usada antes:
  max p * sum(v) - transporte - custo fixo prensas - custo operacional (o * t * visita)
"""

import numpy as np
import json
from gurobipy import Model, GRB

# -------- CONFIG ----------
USE_ALL_PRESSES = False   # Se True => força z[i]==1 para todas as prensas
TIME_LIMIT = 120          # segundos, 0 para sem limite
WRITE_IIS = True          # se infeasible, exportará IIS (gurobi .ilp)
# --------------------------

# parâmetros econômicos / problema
p = 120.0  # preço por tonelada
deposito = 0

# -------- load data (.npy gerados por seu script) ----------
print("Carregando dados .npy...")
c = np.load("c_ijk.npy")        # (m,n,n)
t = np.load("t_ij.npy")         # (m,n) minutos (processamento)
TD = np.load("TD_jk.npy")       # (n,n) (opcional)
S = np.load("S.npy")            # (n,)
f = np.load("f.npy")            # (m,)
o = np.load("o.npy")            # (m,)
# capacidade por prensa (opcional)
try:
    cap_pressa = np.load("capacidade_i.npy")
except:
    cap_pressa = None

m, n = t.shape
print(f"m={m}, n={n}")
print("Dados carregados.\n")

# --------- model ----------
model = Model("VRP_1trip_per_press")

# variables
x = model.addVars(m, n, n, vtype=GRB.BINARY, name="x")   # arco i,j->k
u = model.addVars(m, n, vtype=GRB.BINARY, name="u")     # prensa i visita j
w = model.addVars(m, n, vtype=GRB.BINARY, name="w")     # prensa i processa j (total)
vvol = model.addVars(n, lb=0.0, ub=S.tolist(), vtype=GRB.CONTINUOUS, name="v")  # volume processado
z = model.addVars(m, vtype=GRB.BINARY, name="z")        # prensa ligada
eta = model.addVars(m, n, lb=0.0, ub=n, vtype=GRB.CONTINUOUS, name="eta")  # MTZ

# Objective
term_receita = sum(p * vvol[j] for j in range(n))
term_transporte = sum(c[i, j, k] * x[i, j, k] for i in range(m) for j in range(n) for k in range(n))
term_fixo = sum(f[i] * z[i] for i in range(m))
term_operacional = sum(o[i] * t[i, j] * u[i, j] for i in range(m) for j in range(n))

model.setObjective(term_receita - term_transporte - term_fixo - term_operacional, GRB.MAXIMIZE)

# -------- Constraints --------

# 0) no self-loops
for i in range(m):
    for j in range(n):
        model.addConstr(x[i, j, j] == 0)

# 1) every non-depot city must be assigned to exactly one prensa (visited exactly once)
for j in range(n):
    if j == deposito:
        # don't force depot assignment across i
        continue
    model.addConstr(sum(u[i, j] for i in range(m)) == 1, name=f"city_assign_{j}")

#2) Cada prensa visita no máximo 5 cidades (excluindo depósito)
for i in range(m):
    model.addConstr(sum(u[i, j] for j in range(n) if j != deposito) <= 5,
                    name=f"max_cities_press_{i}")


# 2) Link visits and arcs:
# For non-depot nodes: sum incoming = sum outgoing = u[i,j]
for i in range(m):
    for j in range(n):
        if j == deposito:
            continue
        model.addConstr(sum(x[i, k, j] for k in range(n)) == u[i, j], name=f"inflow_eq_u_{i}_{j}")
        model.addConstr(sum(x[i, j, k] for k in range(n)) == u[i, j], name=f"outflow_eq_u_{i}_{j}")

# 3) Depot entry/exit: each prensa if active must leave from depot once and return once
for i in range(m):
    model.addConstr(sum(x[i, deposito, k] for k in range(n)) == z[i], name=f"depot_exit_{i}")
    model.addConstr(sum(x[i, k, deposito] for k in range(n)) == z[i], name=f"depot_enter_{i}")

# 4) Link arcs -> visits (if an arc exists then both endpoints are visited by that press)
for i in range(m):
    for j in range(n):
        for k in range(n):
            model.addConstr(x[i, j, k] <= u[i, j])
            model.addConstr(x[i, j, k] <= u[i, k])

# 5) w only if visit
for i in range(m):
    for j in range(n):
        model.addConstr(w[i, j] <= u[i, j])

# 6) each city processed exactly once (full processing)
for j in range(n):
    if j == deposito:
        model.addConstr(sum(w[i, j] for i in range(m)) == 0)
    else:
        model.addConstr(sum(w[i, j] for i in range(m)) == 1, name=f"process_once_{j}")

# 7) volume link
for j in range(n):
    if j == deposito:
        model.addConstr(vvol[j] == 0)
    else:
        model.addConstr(vvol[j] == S[j] * sum(w[i, j] for i in range(m)), name=f"vol_link_{j}")

# 8) z linked to visits: if any visit by i then z[i]=1
for i in range(m):
    model.addConstr(sum(u[i, j] for j in range(n)) <= n * z[i])

# 9) MTZ elimination of sub-tours (nodes 1..n-1)
for i in range(m):
    for j in range(1, n):
        for k in range(1, n):
            if j == k:
                continue
            model.addConstr(eta[i, j] - eta[i, k] + n * x[i, j, k] <= n - 1)

# 10) optional: force all presses used (if requested)
if USE_ALL_PRESSES:
    for i in range(m):
        model.addConstr(z[i] == 1)

# --- solver params
if TIME_LIMIT and TIME_LIMIT > 0:
    model.setParam("TimeLimit", TIME_LIMIT)
model.setParam("MIPGap", 1e-1)

# solve
print("Otimização iniciada...")
model.optimize()

# If infeasible -> compute IIS and export
if model.Status == GRB.INFEASIBLE:
    print("Modelo INVIÁVEL. Gerando IIS...")
    model.computeIIS()
    iis_name = "model_IIS.ilp"
    model.write(iis_name)
    print("IIS escrito em", iis_name)
    # still attempt to export an empty JSON describing infeasibility
    summary = {"status": int(model.Status), "objective": None, "used_presses": [], "routes": []}
    with open("solution_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Arquivo solution_summary.json salvo (inviável).")
    raise SystemExit(1)

# Export solution (if feasible or suboptimal)
# Tenta obter o objective value mesmo com TIME_LIMIT
obj_value = None
if model.Status in (GRB.OPTIMAL, GRB.SUBOPTIMAL):
    obj_value = float(model.ObjVal)
elif model.Status == GRB.TIME_LIMIT:
    # Quando tempo limite é atingido, tenta pegar o best objective encontrado
    try:
        obj_value = float(model.ObjVal)
    except:
        obj_value = None

summary = {
    "status": int(model.Status),
    "objective": obj_value,
    "used_presses": [],
    "routes": []
}

def reconstruct_route_local(x_mat):
    succ = {}
    for a in range(n):
        for b in range(n):
            if x_mat[a, b] > 0.5:
                succ.setdefault(a, []).append(b)
    # walk from depot
    route = [deposito]
    cur = deposito
    visited = set()
    while True:
        nxts = succ.get(cur, [])
        if not nxts:
            break
        # prefer non-visited non-depot
        nxt = None
        for cand in nxts:
            if cand != deposito and cand not in visited:
                nxt = cand
                break
        if nxt is None:
            nxt = nxts[0]
        route.append(int(nxt))
        if nxt == deposito:
            break
        visited.add(nxt)
        cur = nxt
        if len(route) > n + 5:
            break
    return route

# collect solution
if model.Status in (GRB.OPTIMAL, GRB.SUBOPTIMAL, GRB.TIME_LIMIT):
    for i in range(m):
        if z[i].X > 0.5:
            summary["used_presses"].append(int(i))
        # build x matrix for this press
        x_local = np.zeros((n, n))
        for j in range(n):
            for k in range(n):
                try:
                    x_local[j, k] = x[i, j, k].X
                except:
                    x_local[j, k] = 0.0
        route = reconstruct_route_local(x_local)
        arcs = [[route[t], route[t+1]] for t in range(len(route)-1)] if len(route) > 1 else []
        # collect volumes for nodes processed by any press
        vols = {}
        for j in range(n):
            try:
                if vvol[j].X > 1e-6:
                    vols[int(j)] = float(vvol[j].X)
            except:
                pass
        summary["routes"].append({
            "pressa": int(i),
            "trip": 0,
            "rota": route,
            "arcos": arcs,
            "volumes": vols
        })

with open("solution_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("Solução salva em solution_summary.json")
print("Status:", model.Status, "Objective:", summary["objective"])
print("Used presses:", summary["used_presses"])
print("Number of routes exported:", len(summary["routes"]))

# Log adicional para TIME_LIMIT
if model.Status == GRB.TIME_LIMIT:
    print("\n" + "="*60)
    print("⏱ TEMPO LIMITE ATINGIDO")
    print("="*60)
    print(f"Best Objective Value encontrado: {summary['objective']}")
    print(f"Gap: {model.MIPGap*100:.2f}%")
    print("="*60)
