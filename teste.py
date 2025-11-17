import numpy as np

# carregar (use os mesmos loaders do seu script)
def load_csv(path, shape=None):
    arr = np.loadtxt(path, delimiter=",")
    return arr.reshape(shape) if shape is not None else arr

COSTS_3D_CSV = "c_ijk.csv"
TIMES_PROC_CSV = "t_ij.csv"
S_CSV = "S.csv"
F_CSV = "f.csv"
O_CSV = "o.csv"

S = load_csv(S_CSV)
f = load_csv(F_CSV)
o = load_csv(O_CSV)
m = f.shape[0]
n = S.shape[0]

c_ijk = load_csv(COSTS_3D_CSV, shape=(m,n,n))
t_ij  = load_csv(TIMES_PROC_CSV, shape=(m,n))

p = 120.0
depot = 0

best_per_city = []
for j in range(n):
    best_profit = -1e12
    best_i = None
    for i in range(m):
        # custo ida e volta aproximado: depot->j + j->depot
        trans_cost = c_ijk[i,depot,j] + c_ijk[i,j,depot]
        op_cost = o[i] * t_ij[i,j]
        fixed = f[i]
        revenue = p * S[j]
        profit = revenue - (trans_cost + op_cost + fixed)
        if profit > best_profit:
            best_profit = profit
            best_i = i
    best_per_city.append((j, best_i, best_profit))
    
# mostrar as cidades com lucro positivo
positivas = [p for p in best_per_city if p[2] > 0]
print("Cidades potencialmente lucrativas (cidade, prensa, lucro):")
for item in sorted(positivas, key=lambda x:-x[2])[:30]:
    print(item)

num_pos = len(positivas)
print(f"\nTotal de cidades com lucro estimado > 0: {num_pos} / {n}")
