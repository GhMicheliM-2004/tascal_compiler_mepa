# mepa_tascal.py — gerador MEPA (Visitor) que consome a AST retornada pelo parser_tascal
from typing import List
import ast_tascal_mepa as ast
from parser_tascal_mepa import tabela_variaveis  # para acessar deslocamentos, se necessário

NIVEL_LEXICO = 0

class GeradorMEPA:
    MEPA_OP = {
        '+': 'SOMA', '-': 'SUBT', '*': 'MULT', '/': 'DIVI',
        'and': 'CONJ', 'or': 'DISJ',
        '=': 'CMIG', '<>': 'CMDG', '<': 'CMME',
        '<=': 'CMEG', '>=': 'CMAG', '>': 'CMMA',
        'not': 'NEGA',
    }

    def __init__(self):
        self.codigo: List[str] = []
        self.rotulo_cont = 0
        self.erros: List[str] = []

    def _novo_rotulo(self) -> str:
        self.rotulo_cont += 1
        return f"R{self.rotulo_cont:02d}"

    def _emite(self, instr: str):
        self.codigo.append(f"     {instr}")

    def _emite_rotulo(self, r: str):
        self.codigo.append(f"{r}: NADA")

    def gera(self, prog: ast.Programa) -> List[str]:
        # cabeçalho
        self._emite("INPP")
        if prog.total_vars > 0:
            self._emite(f"AMEM {prog.total_vars}")
        # visitar bloco
        self.visita(prog.bloco)
        # fim
        self._emite("PARA")
        self._emite("FIM")
        return self.codigo

    def visita(self, node):
        m = 'visita_' + node.__class__.__name__
        fn = getattr(self, m, None)
        if fn is None:
            # silently ignore unknown nodes
            return
        return fn(node)

    def visita_BlocoCmds(self, bloco: ast.BlocoCmds):
        for cmd in bloco.lista_cmds:
            self.visita(cmd)

    def visita_Declaracao(self, decl: ast.Declaracao):
        # nada a emitir (AMEM no header). Mantemos declaração para compatibilidade.
        return

    def visita_Atribuicao(self, cmd: ast.Atribuicao):
        # gerar expressão
        self.visita(cmd.expr)
        # armazenar no endereço da variável
        simb = None
        if isinstance(cmd.id, ast.CalcId):
            simb = cmd.id.simbolo
            if simb is None and cmd.id.nome in tabela_variaveis:
                simb = tabela_variaveis[cmd.id.nome]
        if simb is None:
            # fallback: emitir comentário
            self._emite(f"; ARMZ ??? (variável não anotada: {cmd.id.nome})")
        else:
            self._emite(f"ARMZ {NIVEL_LEXICO},{simb.desloc}")

    def visita_Leitura(self, cmd: ast.Leitura):
        for cid in cmd.ids:
            # emitir LEIT + ARMZ desloc
            self._emite("LEIT")
            simb = cid.simbolo
            if simb is None and cid.nome in tabela_variaveis:
                simb = tabela_variaveis[cid.nome]
            if simb is None:
                self._emite(f"; ARMZ ??? (variável não anotada: {getattr(cid,'nome',cid)})")
            else:
                self._emite(f"ARMZ {NIVEL_LEXICO},{simb.desloc}")

    def visita_Escrita(self, cmd: ast.Escrita):
        for e in cmd.exprs:
            self.visita(e)
            self._emite("IMPR")

    def visita_Condicional(self, cmd: ast.Condicional):
        r_else = self._novo_rotulo()
        r_end = self._novo_rotulo()
        # condição
        self.visita(cmd.cond)
        self._emite(f"DSVF {r_else}")
        # then
        self.visita(cmd.then_cmd)
        self._emite(f"DSVS {r_end}")
        # else label
        self._emite_rotulo(r_else)
        if cmd.else_cmd:
            self.visita(cmd.else_cmd)
        # end label
        self._emite_rotulo(r_end)

    def visita_Enquanto(self, cmd: ast.Enquanto):
        r_begin = self._novo_rotulo()
        r_false = self._novo_rotulo()
        self._emite_rotulo(r_begin)
        self.visita(cmd.cond)
        self._emite(f"DSVF {r_false}")
        self.visita(cmd.bloco)
        self._emite(f"DSVS {r_begin}")
        self._emite_rotulo(r_false)

    def visita_Repete(self, cmd: ast.Repete):
        r_begin = self._novo_rotulo()
        self._emite_rotulo(r_begin)
        self.visita(cmd.bloco)
        self.visita(cmd.cond)
        self._emite(f"DSVF {r_begin}")

    # ---------- EXPRESSÕES ----------
    def visita_CalculoBinario(self, expr: ast.CalculoBinario):
        self.visita(expr.left)
        self.visita(expr.right)
        op = expr.op
        mnem = self.MEPA_OP.get(op)
        if mnem:
            self._emite(mnem)
        else:
            # suportar tokens escritos com nomes diferentes (por exemplo 'MAIS' vs '+')
            # tentar mapear símbolos usuais
            if op == '+':
                self._emite("SOMA")
            elif op == '-':
                self._emite("SUBT")
            elif op == '*':
                self._emite("MULT")
            elif op in ('/', 'DIV'):
                self._emite("DIVI")
            else:
                self._emite(f"; Operador não mapeado: {op}")

    def visita_CalculoUnario(self, expr: ast.CalculoUnario):
        if expr.op == '-':
            # -x -> avaliar x, multiplicar por -1
            self.visita(expr.operand)
            self._emite("CRCT -1")
            self._emite("MULT")
        elif expr.op == 'not':
            # not x -> avaliar x; NEGA (se sua MEPA tiver NEGA)
            self.visita(expr.operand)
            mnem = self.MEPA_OP.get('not', None)
            if mnem:
                self._emite(mnem)
            else:
                # alternativa: CRCT 0 ; CMIG  (x == 0)
                self._emite("CRCT 0")
                self._emite("CMIG")
        else:
            self._emite(f"; unário desconhecido {expr.op}")

    def visita_CalcId(self, idnode: ast.CalcId):
        simb = idnode.simbolo
        if simb is None and idnode.nome in tabela_variaveis:
            simb = tabela_variaveis[idnode.nome]
        if simb is None:
            self._emite(f"; CRVL ??? (variável não anotada: {idnode.nome})")
        else:
            self._emite(f"CRVL {NIVEL_LEXICO},{simb.desloc}")

    def visita_CalcConstNum(self, c: ast.CalcConstNum):
        self._emite(f"CRCT {c.valor}")

    def visita_CalcConstBool(self, c: ast.CalcConstBool):
        v = 1 if c.valor else 0
        self._emite(f"CRCT {v}")
