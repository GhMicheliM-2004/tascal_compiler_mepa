from __future__ import annotations
from dataclasses import dataclass
import ast_cldin2 as ast

class Tipo:...

@dataclass(frozen=True)
class TipoReal(Tipo):
    def __str__(self) -> str: return "real"

@dataclass(frozen=True)
class TipoBool(Tipo):
    def __str__(self) -> str: return "booleano"

TIPO_REAL = TipoReal()
TIPO_BOOL = TipoBool()

class Categoria:
    VAR = 'var'

@dataclass
class Simbolo:
    nome: str
    cat: str
    tipo: Tipo | None = None
    deslocamento: int = 0

# Visitor genérico
class Visitador:
    def visita(self, no: ast.No):
        if no is None:
            return
        nome_metodo = f'visita_{type(no).__name__}'
        visitor = getattr(self, nome_metodo, self.visita_padrao)
        return visitor(no)

    def visita_padrao(self, no: ast.No):
        raise NotImplementedError(f"visita_{type(no).__name__} não foi implementada.")