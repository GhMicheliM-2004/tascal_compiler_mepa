# Gerador MEPA que consome a AST retornada pelo parser_tascal_mepa.py
from typing import List
import ast_tascal_mepa as ast
import parser_tascal_mepa  # para acessar deslocamentos, se necessário

NIVEL_LEXICO = 0 # nível léxico fixo para variáveis globais

class GeradorMEPA: # gerador de código MEPA
    MEPA_OP = {
        '+': 'SOMA', '-': 'SUBT', '*': 'MULT', '/': 'DIVI', 'div': 'DIVI',
        'and': 'CONJ', 'or': 'DISJ', 'not': 'NEGA',
        '=': 'CMIG', '<>': 'CMDG', '<': 'CMME',
        '<=': 'CMEG', '>=': 'CMAG', '>': 'CMMA',
    }

    def __init__(self): # inicializa gerador
        self.codigo: List[str] = []
        self.rotulo_cont = 0
        self.erros: List[str] = []

    def _novo_rotulo(self) -> str: # gera novo rótulo
        self.rotulo_cont += 1
        return f"R{self.rotulo_cont:02d}"

    def _emite(self, instr: str): # emite instrução MEPA
        self.codigo.append(f"     {instr}")

    def _emite_rotulo(self, r: str): # emite rótulo MEPA
        self.codigo.append(f"{r}: NADA")

    def gera(self, prog: ast.Programa) -> List[str]: # gera código MEPA para o programa
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

    def visita(self, node): # visita nó da AST
        m = 'visita_' + node.__class__.__name__
        fn = getattr(self, m, None)
        if fn is None:
            return
        return fn(node)

    def visita_BlocoCmds(self, bloco: ast.BlocoCmds): # visita bloco de comandos
        for cmd in bloco.lista_cmds:
            self.visita(cmd)

    def visita_Declaracao(self, decl: ast.Declaracao): # visita declaração 
        return

    def visita_Atribuicao(self, cmd: ast.Atribuicao): # visita comando de atribuição
        # gerar expressão
        self.visita(cmd.expr)
        # armazenar no endereço da variável
        simb = None
        if isinstance(cmd.id, ast.CalcId): # pode ser CalcId ou outro tipo de nó
            simb = cmd.id.simbolo
            if simb is None and cmd.id.nome in parser_tascal_mepa.tabela_variaveis:
                simb = parser_tascal_mepa.tabela_variaveis[cmd.id.nome]
        if simb is None:
            self._emite(f"; ARMZ ??? (variável não anotada: {cmd.id.nome})")
        else:
            self._emite(f"ARMZ {NIVEL_LEXICO},{simb.desloc}")

    def visita_Leitura(self, cmd: ast.Leitura): # visita comando de leitura
        for cid in cmd.ids:
            self._emite("LEIT")
            simb = cid.simbolo
            if simb is None and cid.nome in parser_tascal_mepa.tabela_variaveis:
                simb = parser_tascal_mepa.tabela_variaveis[cid.nome]
            if simb is None:
                self._emite(f"; ARMZ ??? (variável não anotada: {getattr(cid,'nome',cid)})")
            else:
                self._emite(f"ARMZ {NIVEL_LEXICO},{simb.desloc}")

    def visita_Escrita(self, cmd: ast.Escrita): # visita comando de escrita
        for e in cmd.exprs:
            self.visita(e)
            self._emite("IMPR")

    def visita_Condicional(self, cmd: ast.Condicional): # visita comando condicional
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

    def visita_Enquanto(self, cmd: ast.Enquanto): # visita comando while
        r_begin = self._novo_rotulo()
        r_false = self._novo_rotulo()
        self._emite_rotulo(r_begin)
        self.visita(cmd.cond)
        self._emite(f"DSVF {r_false}")
        self.visita(cmd.bloco)
        self._emite(f"DSVS {r_begin}")
        self._emite_rotulo(r_false)

    def visita_CalculoBinario(self, expr: ast.CalculoBinario): # visita cálculo binário
        self.visita(expr.left)
        self.visita(expr.right)
        op = expr.op
        op_norm = op.lower() if isinstance(op, str) else str(op)
        mnem = self.MEPA_OP.get(op_norm)
        if mnem:
            self._emite(mnem)
        else:
            if op_norm == '+':
                self._emite("SOMA")
            elif op_norm == '-':
                self._emite("SUBT")
            elif op_norm == '*':
                self._emite("MULT")
            elif op_norm in ('/', 'div'):
                self._emite("DIVI")
            else:
                self._emite(f"; Operador não mapeado: {op}")
                self.erros.append(f"Operador não mapeado: {op}")
                
    def visita_CalculoUnario(self, expr: ast.CalculoUnario): # visita cálculo unário
        if expr.op == '-':
            self.visita(expr.operand)
            self._emite("CRCT -1")
            self._emite("MULT")
        elif expr.op == 'not':
            self.visita(expr.operand)
            mnem = self.MEPA_OP.get('not', None)
            if mnem:
                self._emite(mnem)
            else:
                self._emite("CRCT 0")
                self._emite("CMIG")
        else:
            self._emite(f"; unário desconhecido {expr.op}")

    def visita_CalcId(self, idnode: ast.CalcId): # visita nó de identificação
        simb = idnode.simbolo
        if simb is None and idnode.nome in parser_tascal_mepa.tabela_variaveis:
            simb = parser_tascal_mepa.tabela_variaveis[idnode.nome]
        if simb is None:
            self._emite(f"; CRVL ??? (variável não anotada: {idnode.nome})")
        else:
            self._emite(f"CRVL {NIVEL_LEXICO},{simb.desloc}")

    def visita_CalcConstNum(self, c: ast.CalcConstNum):
        self._emite(f"CRCT {c.valor}")

    def visita_CalcConstBool(self, c: ast.CalcConstBool):
        v = 1 if c.valor else 0
        self._emite(f"CRCT {v}")
