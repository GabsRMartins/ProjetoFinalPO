import numpy as np

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
np.save("c_ijk.npy", c_ijk)
np.save("t_ij.npy", t_ij)
np.save("TD_jk.npy", TD_jk)
np.save("S.npy", S)
np.save("f.npy", f)
np.save("o.npy", o)
np.save("capacidade_i.npy", capacidade_i)

# also save CSV for interoperability if needed:
np.savetxt("S.csv", S, delimiter=",", fmt="%.2f")
np.savetxt("f.csv", f, delimiter=",", fmt="%.2f")
np.savetxt("o.csv", o, delimiter=",", fmt="%.2f")
