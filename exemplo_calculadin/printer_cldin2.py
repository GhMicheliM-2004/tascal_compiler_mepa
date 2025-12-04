from __future__ import annotations
import ast_cldin2 as ast
from defs_cldin2 import Visitador
import sys

class ImpressoraAST(Visitador):
    def __init__(self, saida=sys.stdout):
        self.saida = saida

    def imprime(self, texto: str):
        self.saida.write(texto)

    def visita_Programa(self, no: ast.Programa):
        self.imprime("(Programa ")
        self.visita(no.bloco_cmds)
        self.imprime(")\n")

    def visita_BlocoCmds(self, no: ast.BlocoCmds):
        self.imprime("(Comandos")
        for cmd in no.lista_cmds:
            self.imprime(" ")
            self.visita(cmd)
        self.imprime(")")

    def visita_Declaracao(self, no: ast.Declaracao):
        self.imprime("(Decl ")
        self.visita(no.id)
        self.imprime(f" : {no.nome_tipo})")

    def visita_Condicional(self, no: ast.Condicional):
        self.imprime("(If ")
        self.visita(no.condicao)
        self.imprime(" ")
        self.visita(no.bloco_then)
        if no.bloco_else:
            self.imprime(" ")
            self.visita(no.bloco_else)
        self.imprime(")")

    def visita_Funcao(self, no: ast.Funcao):
        self.imprime(f"({no.nome_funcao.upper()} ")
        self.visita(no.argumento)
        self.imprime(")")

    def visita_Atribuicao(self, no: ast.Atribuicao):
        self.imprime("(Atrib ")
        self.visita(no.id)
        self.imprime(" ")
        self.visita(no.calculo)
        self.imprime(")")

    def visita_CalculoBinario(self, no: ast.CalculoBinario):
        self.imprime("(CalcBin ")
        self.visita(no.esq)
        self.imprime(f" {no.op} ")
        self.visita(no.dir)
        self.imprime(")")

    def visita_CalculoUnario(self, no: ast.CalculoUnario):
        self.imprime(f"(CalcUn {no.op} ")
        self.visita(no.calculo)
        self.imprime(")")

    def visita_CalcId(self, no: ast.CalcId):
        self.imprime(f"(Id {no.nome})")

    def visita_CalcConstNum(self, no: ast.CalcConstNum):
        self.imprime(f"(ConstNum {repr(no.valor)})")

    def visita_CalcConstBool(self, no: ast.CalcConstBool):
        self.imprime(f"(ConstBool {repr(no.valor)})")
    
