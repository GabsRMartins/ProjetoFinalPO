# LEIA-ME - Problema de Roteamento de Veículos (VRP)

## 📋 Descrição do Projeto

Este projeto implementa uma solução para o Problema de Roteamento de Veículos (Vehicle Routing Problem - VRP) utilizando otimização linear inteira mista com o solver Gurobi. O sistema otimiza a alocação de prensas a cidades, maximizando o lucro considerando custos de transporte, custos fixos e custos operacionais.

---

## 🔧 Pré-requisitos

### Software Necessário:
- **Python 3.8+** (recomendado Python 3.10 ou superior)
- **Gurobi Optimizer** (com licença válida)
- **Bibliotecas Python**:
  - `gurobipy` (solver de otimização)
  - `numpy` (manipulação de arrays)
  - `matplotlib` (visualização)

### Instalação das Dependências:

```bash
pip install gurobipy numpy matplotlib
```

**Nota:** O Gurobi requer uma licença. Para uso acadêmico, obtenha uma licença gratuita em: https://www.gurobi.com/academia/academic-program-and-licenses/

---

## 📂 Estrutura do Projeto

```
ProjetoFinalPO/
│
├── files.py                    # Geração de dados de entrada
├── alg.py                      # Algoritmo de otimização VRP
├── visualizar_rotas.py         # Visualização das rotas
├── start.py                    # Script de execução automática
├── LEIA-ME.md                  # Este arquivo
│
├── data/                       # Dados gerados (criado automaticamente)
│   ├── c_ijk.npy              # Custos de transporte
│   ├── t_ij.npy               # Tempos de processamento
│   ├── S.npy                  # Volumes das cidades
│   ├── f.npy                  # Custos fixos das prensas
│   ├── o.npy                  # Custos operacionais
│   └── capacidade_i.npy       # Capacidades das prensas
│
├── solution_summary.json       # Solução encontrada pelo otimizador
│
└── graficos_separados/         # Visualizações geradas
    └── X_prensas_Y_cidades/
        ├── 00_grafico_completo.png
        ├── 01_prensa_0.png
        ├── 02_prensa_1.png
        ├── ...
        └── RESUMO.txt
```

---

## 🚀 Como Executar o Programa

### **Opção 1: Execução Automática (Recomendado)**

Execute o script `start.py` que executará todos os passos automaticamente:

```bash
python start.py
```

Este script executa na ordem:
1. **files.py** - Gera os arquivos de dados
2. **alg.py** - Executa o modelo de otimização
3. **visualizar_rotas.py** - Gera as visualizações

**Vantagens:**
- ✅ Execução automatizada
- ✅ Verificação de erros entre etapas
- ✅ Log completo da execução
- ✅ Relatório de tempo e sucesso

---

### **Opção 2: Execução Manual (Passo a Passo)**

Execute cada arquivo individualmente na ordem correta:

#### **Passo 1: Gerar Dados de Entrada**
```bash
python files.py
```
**O que faz:**
- Gera matrizes de custos, tempos e volumes
- Cria o diretório `data/` com arquivos `.npy` e `.csv`

**Saída esperada:**
```
Dados salvos em data/
```

---

#### **Passo 2: Executar Otimização**
```bash
python alg.py
```
**O que faz:**
- Carrega os dados gerados
- Constrói o modelo de otimização VRP
- Resolve usando Gurobi
- Exporta solução para `solution_summary.json`

**Parâmetros configuráveis em `alg.py`:**
```python
USE_ALL_PRESSES = False   # Forçar uso de todas as prensas
TIME_LIMIT = 600          # Tempo limite em segundos (0 = sem limite)
WRITE_IIS = True          # Escrever IIS se inviável
```

**Saída esperada:**
```
Otimização iniciada...
Status: 2 Objective: 10000.0
Used presses: [0, 1, 2, ...]
Solução salva em solution_summary.json
```

**Códigos de Status do Gurobi:**
- `2` = OPTIMAL (solução ótima encontrada)
- `9` = TIME_LIMIT (tempo limite atingido, melhor solução salva)
- `3` = INFEASIBLE (problema inviável)

---

#### **Passo 3: Visualizar Resultados**
```bash
python visualizar_rotas.py
```
**O que faz:**
- Lê `solution_summary.json`
- Gera gráficos das rotas de todas as prensas
- Cria gráficos individuais por prensa
- Salva arquivos PNG e resumo em texto

**Saída esperada:**
```
Prensas usadas: [0, 1, 2, ...]
Gerando gráfico completo...
✓ Gráfico completo salvo em: graficos_separados/.../00_grafico_completo.png
✓ Gráfico da Prensa 0 salvo em: graficos_separados/.../01_prensa_0.png
...
✓ PROCESSO CONCLUÍDO COM SUCESSO!
```

---

## 📊 Arquivos de Saída

### **1. solution_summary.json**
Arquivo JSON com a solução encontrada:
```json
{
  "status": 2,
  "objective": 10000.0,
  "used_presses": [0, 1, 2, ...],
  "routes": [
    {
      "prensa": 0,
      "trip": 0,
      "rota": [0, 29, 4, 44, 24, 2, 0],
      "arcos": [[0, 29], [29, 4], ...],
      "volumes": {"1": 75.0, "2": 177.0, ...}
    },
    ...
  ]
}
```

**Campos:**
- `status`: Código de status do Gurobi
- `objective`: Valor objetivo (lucro) da solução
- `used_presses`: Lista de IDs das prensas utilizadas
- `routes`: Detalhes de cada rota (prensa, cidades visitadas, arcos, volumes)

---

### **2. Gráficos Gerados**

#### **00_grafico_completo.png**
- Visão geral com todas as rotas
- Todas as prensas em cores diferentes
- Legenda completa
- Lucro total no título

#### **XX_prensa_N.png** (um por prensa)
- Mapa da rota com arcos destacados
- Números das cidades visíveis
- Informações detalhadas (cidades visitadas, arcos)
- Legenda específica da prensa

---

### **3. RESUMO.txt**
Arquivo de texto com:
- Estatísticas gerais (prensas, objetivo, rotas)
- Detalhes por prensa (arcos, cidades, rota)
- Lista de arquivos gerados

---

## ⚙️ Configurações Avançadas

### **Modificar Parâmetros do Problema**

Edite o arquivo **`files.py`**:
```python
m = 10  # Número de prensas
n = 50  # Número de cidades
```

### **Ajustar Tempo Limite de Otimização**

Edite o arquivo **`alg.py`**:
```python
TIME_LIMIT = 600  # 10 minutos (em segundos)
```

### **Forçar Uso de Todas as Prensas**

Edite o arquivo **`alg.py`**:
```python
USE_ALL_PRESSES = True
```

---

## ❗ Solução de Problemas

### **Erro: "Gurobi license not found"**
**Solução:** Instale e configure uma licença válida do Gurobi.
- Para uso acadêmico: https://www.gurobi.com/academia/

### **Erro: "ModuleNotFoundError: No module named 'gurobipy'"**
**Solução:** Instale as dependências:
```bash
pip install gurobipy numpy matplotlib
```

### **Erro: "FileNotFoundError: solution_summary.json"**
**Solução:** Execute `alg.py` antes de `visualizar_rotas.py`:
```bash
python alg.py
python visualizar_rotas.py
```

### **Modelo retorna STATUS = 3 (INFEASIBLE)**
**Possíveis causas:**
- Restrições muito rígidas
- Dados inconsistentes
- Número insuficiente de prensas para o número de cidades

**Solução:** 
- Aumente o número de prensas em `files.py`
- Revise as restrições em `alg.py`
- Verifique o arquivo `model_IIS.ilp` gerado para identificar restrições conflitantes

### **Tempo limite atingido (STATUS = 9)**
**Comportamento:** O solver salva a melhor solução encontrada até o momento.

**Para melhorar:**
- Aumente `TIME_LIMIT` em `alg.py`
- Ajuste `MIPGap` para aceitar soluções com maior gap de otimalidade

---

## 📈 Interpretação dos Resultados

### **Valor Objetivo (Lucro)**
- Representa: Receita - Custos de Transporte - Custos Fixos - Custos Operacionais
- Quanto maior, melhor a solução

### **Prensas Utilizadas**
- Lista de IDs das prensas ativas na solução
- Prensas não utilizadas têm `z[i] = 0`

### **Rotas**
- Cada rota começa e termina no depósito (cidade 0)
- Arcos mostram a sequência de movimentação
- Volumes indicam a quantidade processada em cada cidade

---

## 📝 Observações Importantes

1. **Seed Aleatória:** Os dados são gerados com `np.random.seed(42)` para reprodutibilidade. Altere para gerar instâncias diferentes.

2. **Coordenadas Simuladas:** As coordenadas das cidades são geradas aleatoriamente apenas para visualização. Os custos reais vêm da matriz `c_ijk`.

3. **Arcos de Retorno:** Arcos tracejados (--) indicam retorno ao depósito.

4. **Números das Cidades:** Começam em 0 (depósito) e vão até n-1.

---

## 📞 Suporte

Para questões sobre:
- **Gurobi:** Consulte a documentação oficial em https://www.gurobi.com/documentation/
- **Problema VRP:** Revise a formulação matemática no código `alg.py`
- **Visualizações:** Verifique os parâmetros de matplotlib em `visualizar_rotas.py`

---

## 📄 Licença

Este projeto é desenvolvido para fins acadêmicos.

---

**Última atualização:** Novembro 2025
**Versão:** 1.0
