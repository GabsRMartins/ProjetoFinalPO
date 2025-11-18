"""
Script para executar o pipeline completo de otimização VRP
Executa os arquivos na ordem: files.py -> alg.py -> visualizar_rotas.py
"""

import subprocess
import sys
import os
from datetime import datetime

def print_header(texto):
    """Imprime um cabeçalho formatado"""
    print("\n" + "=" * 70)
    print(f"  {texto}")
    print("=" * 70 + "\n")

def executar_script(nome_arquivo, descricao):
    """
    Executa um script Python e retorna True se bem-sucedido
    """
    print_header(f"EXECUTANDO: {descricao}")
    print(f"Arquivo: {nome_arquivo}")
    print(f"Horário: {datetime.now().strftime('%H:%M:%S')}\n")
    
    try:
        # Executa o script usando o mesmo interpretador Python
        resultado = subprocess.run(
            [sys.executable, nome_arquivo],
            check=True,
            capture_output=False,
            text=True
        )
        
        print(f"\n✓ {nome_arquivo} executado com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ ERRO ao executar {nome_arquivo}")
        print(f"Código de erro: {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n✗ ERRO: Arquivo {nome_arquivo} não encontrado!")
        return False
    except Exception as e:
        print(f"\n✗ ERRO inesperado: {str(e)}")
        return False

def main():
    """
    Função principal que executa o pipeline completo
    """
    print_header("PIPELINE DE OTIMIZAÇÃO VRP - INÍCIO")
    print(f"Data e hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Diretório atual: {os.getcwd()}\n")
    
    # Define os scripts a serem executados
    scripts = [
        ("files.py", "Geração de arquivos de dados"),
        ("alg.py", "Otimização do modelo VRP"),
        ("visualizar_rotas.py", "Visualização das rotas")
    ]
    
    inicio = datetime.now()
    sucessos = []
    falhas = []
    
    # Executa cada script sequencialmente
    for arquivo, descricao in scripts:
        if executar_script(arquivo, descricao):
            sucessos.append(arquivo)
        else:
            falhas.append(arquivo)
            print(f"\n⚠ Pipeline interrompido devido a erro em {arquivo}")
            break
    
    # Resumo da execução
    fim = datetime.now()
    duracao = (fim - inicio).total_seconds()
    
    print_header("RESUMO DA EXECUÇÃO")
    print(f"Tempo total: {duracao:.2f} segundos")
    print(f"\nScripts executados com sucesso ({len(sucessos)}/{len(scripts)}):")
    for arquivo in sucessos:
        print(f"  ✓ {arquivo}")
    
    if falhas:
        print(f"\nScripts com falha ({len(falhas)}/{len(scripts)}):")
        for arquivo in falhas:
            print(f"  ✗ {arquivo}")
    
    print_header("PIPELINE FINALIZADO")
    
    if len(sucessos) == len(scripts):
        print("✓ Todos os scripts foram executados com sucesso!")
        print("\nResultados disponíveis em:")
        print("  - solution_summary.json (solução do modelo)")
        print("  - graficos_separados/ (visualizações)")
        return 0
    else:
        print("✗ Pipeline finalizado com erros.")
        return 1

if __name__ == "__main__":
    codigo_saida = main()
    sys.exit(codigo_saida)
