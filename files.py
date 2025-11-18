import numpy as np
import os

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

m = 12
n = 60
np.random.seed(42)

c_ijk = np.random.uniform(500, 5000, size=(m,n,n))
S = np.random.randint(50,500,size=n)
capacidade_i = np.random.uniform(5,10,size=m)
t_ij = np.zeros((m,n))
for i in range(m):
    for j in range(n):
        horas = S[j] / capacidade_i[i]
        t_ij[i,j] = horas  

TD_jk = np.random.uniform(20,300,size=(n,n))
f = np.random.uniform(1000,5000,size=m)
o = np.random.uniform(1,10,size=m)

# SAVE as .npy (robusto)
np.save("data/c_ijk.npy", c_ijk)
np.save("data/t_ij.npy", t_ij)
np.save("data/TD_jk.npy", TD_jk)
np.save("data/S.npy", S)
np.save("data/f.npy", f)
np.save("data/o.npy", o)
np.save("data/capacidade_i.npy", capacidade_i)

# also save CSV for interoperability if needed:
np.savetxt("data/S.csv", S, delimiter=",", fmt="%.2f")
np.savetxt("data/f.csv", f, delimiter=",", fmt="%.2f")
np.savetxt("data/o.csv", o, delimiter=",", fmt="%.2f")
