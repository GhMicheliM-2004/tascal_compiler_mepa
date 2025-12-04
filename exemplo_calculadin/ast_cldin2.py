from __future__ import annotations
from dataclasses import dataclass
from typing import List
from defs_cldin2 import Tipo, Simbolo

class No:...

class Cmd(No):...

class Calculo(No):
    tipo: Tipo | None = None
 
@dataclass
class Programa(No):
    bloco_cmds: BlocoCmds
    # anotação
    total_vars: int = 0

@dataclass
class BlocoCmds(No):
    lista_cmds: List[Cmd]

@dataclass
class Declaracao(Cmd):
    nome_tipo: str
    id: CalcId

@dataclass
class Condicional(Cmd):
    condicao: Calculo
    bloco_then: BlocoCmds
    bloco_else: BlocoCmds | None

@dataclass
class Funcao(Cmd):
    nome_funcao: str
    argumento: CalcId

@dataclass
class Atribuicao(Cmd):
    id: CalcId
    calculo: Calculo

# Filhos de Calculo - herdam tipo
@dataclass
class CalculoBinario(Calculo):
    esq: Calculo
    op: str
    dir: Calculo

@dataclass
class CalculoUnario(Calculo):
    op: str
    calculo: Calculo

@dataclass
class CalcId(Calculo):
    nome: str
    # anotação
    simbolo: Simbolo | None = None

@dataclass
class CalcConstNum(Calculo):
    valor: float

@dataclass
class CalcConstBool(Calculo):
    valor: bool