from __future__ import annotations
from typing import List
import ast_cldin2 as ast
from defs_cldin2 import Visitador

NIVEL_LEXICO = 0

class GeradorDeCodigo(Visitador):
    MEPA_OP = {
        '+': 'SOMA', '-': 'SUBT', '*': 'MULT', '/': 'DIVI',
        'and': 'CONJ', 'or': 'DISJ',
        '==': 'CMIG', '!=': 'CMDG', '<': 'CMME',
        '<=': 'CMEG', '>': 'CMMA', '>=': 'CMAG',
        'not': 'NEGA',
    }

    def __init__(self):
        self.codigo: List[str] = []
        self.erros: List[str] = []
        self.tem_erro = False
        self.contador_rotulos: int = 0        

    def _erro(self, msg: str):
        self.erros.append(f"Erro de geração: {msg}")
        self.tem_erro = True
        
    def _emite(self, instrucao: str):
        self.codigo.append(f"     {instrucao}")
    
    def _emite_rotulo(self, rotulo: str):
        self.codigo.append(f"{rotulo}: NADA")
        
    def _novo_rotulo(self) -> str:
        self.contador_rotulos += 1
        return f"R{self.contador_rotulos:02d}"

    def visita_Programa(self, prog: ast.Programa):
        self._emite("INPP") 
        
        if prog.total_vars > 0:
            self._emite(f"AMEM {prog.total_vars}") 
        
        self.visita(prog.bloco_cmds)
        
        self._emite("PARA") 
        self._emite("FIM") 

    def visita_BlocoCmds(self, bloco: ast.BlocoCmds):
        for cmd in bloco.lista_cmds:
            self.visita(cmd)

    def visita_Declaracao(self, decl: ast.Declaracao):
        # A alocação é feita em visita_Programa
        pass 

    def visita_Atribuicao(self, cmd: ast.Atribuicao):
        self.visita(cmd.calculo)
        
        simbolo = cmd.id.simbolo
        if simbolo and simbolo.deslocamento is not None:
            self._emite(f"ARMZ {NIVEL_LEXICO},{simbolo.deslocamento}") 
        else:
            self._erro(f"Deslocamento da variável de atribuição não encontrado.")
            return

    def visita_Condicional(self, cmd: ast.Condicional):
        rotulo_else = self._novo_rotulo()
        rotulo_fim_if = self._novo_rotulo()
        
        self.visita(cmd.condicao)
        
        if cmd.bloco_else:
            self._emite(f"DSVF {rotulo_else}")
            self.visita(cmd.bloco_then)
            self._emite(f"DSVS {rotulo_fim_if}")
            
            self._emite_rotulo(rotulo_else)
            self.visita(cmd.bloco_else)
        else:
            self._emite(f"DSVF {rotulo_fim_if}")
            self.visita(cmd.bloco_then)
        
        self._emite_rotulo(rotulo_fim_if)

    def visita_Funcao(self, func: ast.Funcao):
        simbolo = func.argumento.simbolo
        if not simbolo or simbolo.deslocamento is None:
            self._erro(f"Variável '{func.argumento.nome}' não anotada.")
            return

        if func.nome_funcao == 'input':
            self._emite("LEIT")
            self._emite(f"ARMZ {NIVEL_LEXICO},{simbolo.deslocamento}")
        
        elif func.nome_funcao == 'output':
            self._emite(f"CRVL {NIVEL_LEXICO},{simbolo.deslocamento}")
            self._emite("IMPR")

    def visita_CalculoBinario(self, calc: ast.CalculoBinario):
        self.visita(calc.esq)
        self.visita(calc.dir)
        
        mepa_inst = self.MEPA_OP[calc.op]
        if mepa_inst:
            self._emite(mepa_inst)
        else:
            self._erro(f"Operador desconhecido {calc.op}")

    def visita_CalculoUnario(self, calc: ast.CalculoUnario):
        self.visita(calc.calculo)
        
        mepa_inst = self.MEPA_OP[calc.op]
        if mepa_inst:
            self._emite(mepa_inst)
        else:
            self._erro(f"Operador unário desconhecido {calc.op}")

    def visita_CalcId(self, id: ast.CalcId):
        simbolo = id.simbolo
        if simbolo and simbolo.deslocamento is not None:
            self._emite(f"CRVL {NIVEL_LEXICO},{simbolo.deslocamento}")
        else:
            self._erro(f"ID '{id.nome}' sem deslocamento.")

    def visita_CalcConstNum(self, const: ast.CalcConstNum):
        self._emite(f"CRCT {const.valor}")

    def visita_CalcConstBool(self, const: ast.CalcConstBool):
        valor_mepa = 1 if const.valor else 0
        self._emite(f"CRCT {valor_mepa}")