# Arquivo para construir a AST
from __future__ import annotations 
from dataclasses import dataclass, field
from typing import List, Optional, Any

# Nó base
class No: #
    pass

# Comando base
class Cmd(No):
    pass

# Expressão base
class Expr(No):
    tipo: Optional[str] = None  # será anotado pela semântica ou por inferência

@dataclass
class Programa(No):
    bloco: 'BlocoCmds'
    nome: Optional[str] = None
    total_vars: int = 0  # será preenchido pelo analisador semântico

@dataclass
class BlocoCmds(No):
    lista_cmds: List[Cmd] = field(default_factory=list)

@dataclass
class Declaracao(Cmd):
    ids: List[str]
    tipo: str  # 'integer' | 'boolean'

@dataclass
class Atribuicao(Cmd):
    id: 'CalcId'
    expr: Expr

@dataclass
class Leitura(Cmd):
    ids: List['CalcId'] 

@dataclass
class Escrita(Cmd):
    exprs: List[Expr]

@dataclass
class Condicional(Cmd):
    cond: Expr
    then_cmd: BlocoCmds
    else_cmd: Optional[BlocoCmds] = None

@dataclass
class Enquanto(Cmd):
    cond: Expr
    bloco: BlocoCmds

@dataclass
class Repete(Cmd):
    bloco: BlocoCmds
    cond: Expr

@dataclass
class CalculoBinario(Expr):
    left: Expr
    op: str
    right: Expr

@dataclass
class CalculoUnario(Expr):
    op: str
    operand: Expr

@dataclass
class CalcId(Expr):
    nome: str
    simbolo: Any = None  # será preenchido com um Simbolo (semântico)

@dataclass
class CalcConstNum(Expr):
    valor: int

@dataclass
class CalcConstBool(Expr):
    valor: bool
