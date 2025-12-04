from __future__ import annotations
from typing import List
import ast_cldin2 as ast
from defs_cldin2 import Visitador, Simbolo, Categoria, Tipo, TIPO_REAL, TIPO_BOOL


class TabelaSimbolos:
    def __init__(self):
        self.tabela = {}
        self.deslocamento_atual: int = 0
    
    def instala(self, s: Simbolo) -> str|None:
        if s.nome in self.tabela:
            return f"Identificador '{s.nome}' já declarado"
        s.deslocamento = self.deslocamento_atual
        self.tabela[s.nome] = s
        self.deslocamento_atual += 1
        return None

    def busca(self, nome) -> Simbolo|None:
        return self.tabela.get(nome, None)
    

class VerificadorSemantico(Visitador):
    def __init__(self) -> None:
        self.ts: TabelaSimbolos = TabelaSimbolos()
        self.erros: List[str] = []
        self.tem_erro: bool = False
        # Controle de escopo: se True, declarações são proibidas
        self.dentro_condicional: bool = False 

    def _erro(self, msg: str):
        self.erros.append(f"{msg}")
        self.tem_erro = True

    def _verifica_tipo_bin(self, op: str, t_esq: Tipo, t_dir: Tipo) -> Tipo|None:
        # Operadores aritméticos: (real, real) -> real
        if op in ('+', '-', '*', '/'):
            if t_esq is not TIPO_REAL or t_dir is not TIPO_REAL:
                self._erro(f"Operador '{op}' exige operandos 'real' (recebeu {t_esq}, {t_dir})")
            return TIPO_REAL
        
        # Operadores lógicos: (bool, bool) -> bool
        if op in ('and', 'or'):
            if t_esq is not TIPO_BOOL or t_dir is not TIPO_BOOL:
                self._erro(f"Operador '{op}' exige operandos 'booleano' (recebeu {t_esq}, {t_dir})")
            return TIPO_BOOL
        
        # Operadores de diferença: (real, real) -> bool OU (bool, bool) -> bool
        if op in ('==', '!='):
            if t_esq is not t_dir:
                self._erro(f"Operador '{op}' não pode comparar tipos diferentes ({t_esq} vs {t_dir})")
            return TIPO_BOOL
        
        # Operadores relacionais: (real, real) -> bool
        if op in ('<', '<=', '>', '>='):
            if t_esq is not TIPO_REAL or t_dir is not TIPO_REAL:
                self._erro(f"Operador '{op}' exige operandos 'real' (recebeu {t_esq}, {t_dir})")
            return TIPO_BOOL
        
        return None

    def _verifica_tipo_unario(self, op: str, t_calculo: Tipo) -> Tipo|None:
        # Operador unário 'not': (bool) -> bool
        if op == 'not':
            if t_calculo is not TIPO_BOOL:
                self._erro(f"Operador 'not' exige 'booleano' (recebeu {t_calculo})")
            return TIPO_BOOL
        return None
    
    # Visitação
    def visita_Programa(self, prog: ast.Programa):
        self.visita(prog.bloco_cmds)
        prog.total_vars = self.ts.deslocamento_atual

    def visita_BlocoCmds(self, bloco: ast.BlocoCmds):
        for cmd in bloco.lista_cmds:
            self.visita(cmd)

    def visita_Declaracao(self, decl: ast.Declaracao):
        if self.dentro_condicional:
            self._erro(f"Declaração da variável '{decl.id.nome}' não permitida dentro de bloco condicional (if/else).")
            return

        if decl.nome_tipo == "real":
            tipo_var = TIPO_REAL
        elif decl.nome_tipo == "bool":
            tipo_var = TIPO_BOOL
        else:
            self._erro(f"Tipo desconhecido '{decl.nome_tipo}' na declaração de '{decl.id.nome}'.")
            return

        simbolo = Simbolo(nome=decl.id.nome, cat=Categoria.VAR, tipo=tipo_var)
        
        erro_instala = self.ts.instala(simbolo)
        if erro_instala:
            self._erro(erro_instala)
            return

        self.visita(decl.id)

    def visita_Atribuicao(self, cmd: ast.Atribuicao):
        self.visita(cmd.calculo)
        self.visita(cmd.id) 
        
        # deu erro em algum lado
        if cmd.id.tipo is None or cmd.calculo.tipo is None:
            return

        tipo_id = cmd.id.tipo
        tipo_calc = cmd.calculo.tipo
        
        if tipo_id is not tipo_calc:
             self._erro(f"Atribuição inválida: Variável '{cmd.id.nome}' é do tipo {tipo_id} e não pode receber valor do tipo {tipo_calc}.")
             return

    def visita_Condicional(self, cmd: ast.Condicional):
        self.visita(cmd.condicao)

        if cmd.condicao.tipo is not TIPO_BOOL:
            self._erro(f"Condição 'if' exige expressão booleana (recebeu {cmd.condicao.tipo}).")

        # Visita os blocos com a flag de escopo ligada
        self.dentro_condicional = True
        self.visita(cmd.bloco_then)
                
        if cmd.bloco_else:
            self.visita(cmd.bloco_else)
        self.dentro_condicional = False

    def visita_Funcao(self, func: ast.Funcao):
        # visita para anotar o CalcId do argumento
        self.visita(func.argumento)

    def visita_CalculoBinario(self, calc: ast.CalculoBinario):
        self.visita(calc.esq)
        self.visita(calc.dir)

        # deu erro em algum lado
        if calc.esq.tipo is None or calc.dir.tipo is None:
            calc.tipo = None
            return

        tipo_resultado = self._verifica_tipo_bin(calc.op, calc.esq.tipo, calc.dir.tipo)
        calc.tipo = tipo_resultado

    def visita_CalculoUnario(self, calc: ast.CalculoUnario):
        self.visita(calc.calculo)

        # deu erro na expressão
        if calc.calculo.tipo is None:
            calc.tipo = None
            return

        tipo_resultado = self._verifica_tipo_unario(calc.op, calc.calculo.tipo)
        calc.tipo = tipo_resultado

    def visita_CalcId(self, id: ast.CalcId):
        simbolo = self.ts.busca(id.nome)
        
        if simbolo is None:
            self._erro(f"Variável '{id.nome}' não foi declarada.")
            id.tipo = None
            return

        # anota o id
        id.tipo = simbolo.tipo
        id.simbolo = simbolo

    def visita_CalcConstNum(self, const: ast.CalcConstNum):
        # anota a const
        const.tipo = TIPO_REAL

    def visita_CalcConstBool(self, const: ast.CalcConstBool):
        # anota a const
        const.tipo = TIPO_BOOL