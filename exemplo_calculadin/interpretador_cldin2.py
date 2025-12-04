# interpretador_cldin2.py
from __future__ import annotations
from typing import List, Dict, Any
import sys

class InterpretadorCalculadin2:
    """
    Interpretador de código intermediário para Calculadin2 (baseado na máquina MEPA, 
    mas adaptado para tipos float e bool).
    """

    def __init__(self):
        # Pilha de execução - Usada para cálculos e passagem de valores
        self.pilha: List[Any] = []
        # Memória de dados - Usada para variáveis (deslocamento)
        self.memoria: List[Any] = []
        # Contador de programa (Program Counter)
        self.pc: int = 0
        # Dicionário de rótulos para saltos
        self.rotulos: Dict[str, int] = {}
        # Instruções do programa
        self.instrucoes: List[List[str]] = []
        # Flag para controlar o estado de execução
        self.em_execucao: bool = True

    def carregar_programa(self, codigo: str):
        """Carrega o código intermediário e resolve os rótulos."""
        linhas = codigo.strip().split('\n')
        
        # Primeira passagem: coleta rótulos
        for i, linha in enumerate(linhas):
            partes = linha.split()
            if not partes:
                continue

            # Rótulo está no início
            if partes[0].endswith(':'):
                rotulo = partes[0][:-1]
                self.rotulos[rotulo] = len(self.instrucoes) # Aponta para a próxima instrução
                # Se for apenas o rótulo, a instrução continua na mesma linha
                if len(partes) > 1:
                    self.instrucoes.append(partes[1:])
            else:
                self.instrucoes.append(partes)

        print(f"Programa carregado com {len(self.instrucoes)} instruções.")
        print(f"Rótulos encontrados: {self.rotulos}")
    
    def _proximo(self):
        """Avança o contador de programa e garante que a execução continua."""
        self.pc += 1
        if self.pc >= len(self.instrucoes):
            self.em_execucao = False

    def executar(self):
        """Inicia o ciclo de interpretação."""
        if not self.instrucoes:
            print("Erro: Nenhum programa carregado.", file=sys.stderr)
            return

        print("\n--- Início da Execução do Calculadin2 ---")
        
        while self.em_execucao and self.pc < len(self.instrucoes):
            try:
                inst = self.instrucoes[self.pc]
                op = inst[0].upper()

                if op == "INPP":
                    # Início do programa
                    self._proximo()

                elif op == "AMEM":
                    # Alocar memória: AMEM <N_VARS>
                    n_vars = int(inst[1])
                    self.memoria = [None] * n_vars
                    print(f"[DEBUG] AMEM {n_vars} -> Memória alocada. Tamanho: {len(self.memoria)}")
                    self._proximo()

                elif op == "CRCT":
                    # Carregar constante: CRCT <VALOR>
                    valor_str = inst[1]
                    try:
                        # Tenta converter para float
                        valor = float(valor_str)
                    except ValueError:
                        # Se falhar, tenta interpretar como booleano (0 ou 1)
                        if valor_str == '1' or valor_str.lower() == 'true':
                            valor = True
                        elif valor_str == '0' or valor_str.lower() == 'false':
                            valor = False
                        else:
                            # Se for uma string não numérica/booleana
                            # valor = valor_str
                            raise ValueError(f"Valor inválido para LEIT.")
                    
                    self.pilha.append(valor)
                    self._proximo()

                elif op == "CRVL":
                    # Carregar Valor: CRVL <NL>,<DESLOCAMENTO>
                    # NL é sempre 0 para Calculadin
                    deslocamento = int(inst[1].split(',')[1])
                    if deslocamento >= len(self.memoria):
                         raise IndexError(f"Acesso de memória inválido (deslocamento {deslocamento}).")
                    
                    valor = self.memoria[deslocamento]
                    if valor is None:
                        raise ValueError(f"Variável no deslocamento {deslocamento} não inicializada.")
                    
                    self.pilha.append(valor)
                    self._proximo()

                elif op == "ARMZ":
                    # Armazenar: ARMZ <NL>,<DESLOCAMENTO>
                    # NL é sempre 0 para Calculadin
                    deslocamento = int(inst[1].split(',')[1])
                    if not self.pilha:
                         raise IndexError("Pilha vazia para instrução ARMZ.")
                    
                    valor = self.pilha.pop()
                    if deslocamento >= len(self.memoria):
                         raise IndexError(f"Acesso de memória inválido (deslocamento {deslocamento}).")
                         
                    self.memoria[deslocamento] = valor
                    self._proximo()

                elif op in ["SOMA", "SUBT", "MULT", "DIVI"]:
                    # Operações aritméticas binárias
                    if len(self.pilha) < 2:
                        raise IndexError(f"Pilha insuficiente para {op}.")
                    
                    dir_val = self.pilha.pop()
                    esq_val = self.pilha.pop()
                    
                    if not isinstance(esq_val, (int, float)) or not isinstance(dir_val, (int, float)):
                        raise TypeError(f"Operação {op} inválida: operandos devem ser numéricos.")

                    if op == "SOMA":
                        res = esq_val + dir_val
                    elif op == "SUBT":
                        res = esq_val - dir_val
                    elif op == "MULT":
                        res = esq_val * dir_val
                    elif op == "DIVI":
                        if dir_val == 0:
                            raise ZeroDivisionError("Divisão por zero.")
                        res = esq_val / dir_val
                    
                    self.pilha.append(res)
                    self._proximo()

                elif op in ["CONJ", "DISJ"]:
                    # Operações lógicas binárias (AND, OR)
                    if len(self.pilha) < 2:
                        raise IndexError(f"Pilha insuficiente para {op}.")
                    
                    dir_val = self.pilha.pop()
                    esq_val = self.pilha.pop()
                    
                    esq_bool = bool(esq_val) if isinstance(esq_val, (int, float)) else esq_val
                    dir_bool = bool(dir_val) if isinstance(dir_val, (int, float)) else dir_val
                    
                    if op == "CONJ": # AND
                        res = esq_bool and dir_bool
                    elif op == "DISJ": # OR
                        res = esq_bool or dir_bool
                    
                    self.pilha.append(res) 
                    self._proximo()

                elif op == "NEGA":
                    # Operação unária (NOT)
                    if not self.pilha:
                        raise IndexError("Pilha vazia para instrução NEGA.")
                    
                    val = self.pilha.pop()
                    val_bool = bool(val) if isinstance(val, (int, float)) else val
                    
                    if not isinstance(val_bool, bool):
                        raise TypeError("Operação NEGA inválida: operando deve ser booleano.")
                        
                    self.pilha.append(not val_bool)
                    self._proximo()

                elif op == "INVR":
                    # Inverter sinal (- unário)
                    if not self.pilha:
                        raise IndexError("Pilha vazia para instrução INVR.")
                    
                    val = self.pilha.pop()
                    
                    if not isinstance(val, (int, float)):
                        raise TypeError("Operação INVR inválida: operando deve ser numérico.")
                        
                    self.pilha.append(-val)
                    self._proximo()

                elif op in ["CMIG", "CMDG", "CMME", "CMEG", "CMMA", "CMAG"]:
                    # Operadores relacionais e de igualdade
                    if len(self.pilha) < 2:
                        raise IndexError(f"Pilha insuficiente para {op}.")
                    
                    dir_val = self.pilha.pop()
                    esq_val = self.pilha.pop()
                    
                    res = False
                    if op == "CMIG": # Igual
                        res = (esq_val == dir_val)
                    elif op == "CMDG": # Diferente
                        res = (esq_val != dir_val)
                    # Comparações relacionais apenas para reais
                    elif isinstance(esq_val, (int, float)) and isinstance(dir_val, (int, float)):
                        if op == "CMME": # Menor
                            res = (esq_val < dir_val)
                        elif op == "CMEG": # Menor ou igual
                            res = (esq_val <= dir_val)
                        elif op == "CMMA": # Maior
                            res = (esq_val > dir_val)
                        elif op == "CMAG": # Maior ou igual
                            res = (esq_val >= dir_val)
                    else:
                        raise TypeError(f"Comparação {op} inválida entre tipos não-numéricos.")

                    # Empilha o resultado booleano (True/False)
                    self.pilha.append(res)
                    self._proximo()

                elif op == "DSVS":
                    # Desvio incondicional: DSVS <ROTULO>
                    rotulo = inst[1]
                    if rotulo not in self.rotulos:
                        raise ValueError(f"Rótulo de salto '{rotulo}' não encontrado.")
                    self.pc = self.rotulos[rotulo] # Atualiza PC
                
                elif op == "DSVF":
                    # Desvio se falso: DSVF <ROTULO>
                    rotulo = inst[1]
                    if not self.pilha:
                        raise IndexError("Pilha vazia para instrução DSVF.")
                    
                    val = self.pilha.pop()
                    val_bool = bool(val) if isinstance(val, (int, float)) else val
                    
                    if not isinstance(val_bool, bool):
                        raise TypeError("DSVF exige valor booleano na pilha.")

                    if not val_bool:
                        if rotulo not in self.rotulos:
                            raise ValueError(f"Rótulo de salto '{rotulo}' não encontrado.")
                        self.pc = self.rotulos[rotulo] # Atualiza PC
                    else:
                        self._proximo()

                elif op == "LEIT":
                    # Leitura (Input)
                    valor_entrada = input("INPUT (real ou booleano): ").strip().lower() # Pede input e normaliza

                    # Tenta converter para float (real)
                    try:
                        valor = float(valor_entrada)
                    
                    # Se falhar, tenta converter para booleano
                    except ValueError:
                        if valor_entrada.upper() == 'TRUE':
                            valor = True
                        elif valor_entrada.upper() == 'FALSE':
                            valor = False
                        else:
                            # Se não for nem real nem booleano válido, trata como erro
                            print(f"Erro de entrada: valor '{valor_entrada}' inválido. Deve ser numérico, 'true' ou 'false'.", file=sys.stderr)
                            # Atribui um valor padrão neutro
                            valor = 0.0 
                    
                    # Empilha o valor convertido (float ou bool)
                    self.pilha.append(valor)
                    self._proximo()

                elif op == "IMPR":
                    # Impressão (Output)
                    if not self.pilha:
                        raise IndexError("Pilha vazia para instrução IMPR.")
                    
                    valor = self.pilha.pop()
                    print(f"OUTPUT: {valor}")
                    self._proximo()

                elif op == "NADA":
                    # Não faz nada
                    self._proximo()

                elif op == "PARA":
                    # Para a execução
                    print("[DEBUG] PARA: Programa finalizado por instrução.")
                    self.em_execucao = False

                elif op == "FIM":
                    # Final
                    self.em_execucao = False

                else:
                    raise ValueError(f"Instrução desconhecida: {op}")

            except Exception as e:
                print(f"Erro de execução na instrução {self.pc} ({' '.join(self.instrucoes[self.pc])}): {e}", file=sys.stderr)
                self.em_execucao = False
        
        print("\n--- Fim da Execução do Calculadin2 ---")
        if self.em_execucao:
             print("Aviso: Fim inesperado do programa (PC fora dos limites).")

def main_interpretador():
    """ Função principal para executar o interpretador. """
    
    if len(sys.argv) != 2:
        print("Modo de uso: python interpretador_cldin2.py <caminho_para_arquivo_ci>", file=sys.stderr)
        sys.exit(1)
        
    caminho_arquivo = sys.argv[1] # Pega o caminho do arquivo .ic
    
    try:
        with open(caminho_arquivo, 'r') as f:
            codigo_mepa = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}", file=sys.stderr)
        sys.exit(1)

    if not codigo_mepa.strip():
        print("Erro: Arquivo de código (.ci) vazio.", file=sys.stderr)
        sys.exit(1)

    interpretador = InterpretadorCalculadin2()
    interpretador.carregar_programa(codigo_mepa)
    interpretador.executar()


if __name__ == "__main__":
    main_interpretador()