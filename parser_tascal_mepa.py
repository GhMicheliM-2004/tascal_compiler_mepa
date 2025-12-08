# parser_tascal.py — parser + semântica (mantém checagens) e agora retorna AST
import ply.yacc as yacc
from lexer_tascal_mepa import tokens
import ast_tascal_mepa as ast

# Tabela de símbolos simples (nome -> tipo/desloc)
class Simbolo:
    def __init__(self, nome: str, tipo: str, desloc: int):
        self.nome = nome
        self.tipo = tipo
        self.desloc = desloc

# estado semântico global (estilo do seu parser original)
tabela_variaveis: dict = {}
erros_semanticos: list = []
_next_desloc = 0
erros_sintaticos: list = []

def semantico_reset():
    global tabela_variaveis, _next_desloc
    tabela_variaveis.clear()
    erros_semanticos.clear()
    erros_sintaticos.clear()
    _next_desloc = 0

def erro_semantico(msg: str, linha: int):
    erro = f"ERRO SEMÂNTICO na linha {linha}: {msg}"
    print(erro)
    erros_semanticos.append(erro)

def instala_programa(nome: str, linha: int):
    # opcional: pode registrar nome (não usado no resto)
    return

def instala_variavel(nome: str, tipo: str, linha: int):
    global tabela_variaveis, _next_desloc
    if nome in tabela_variaveis:
        erro_semantico(f"variável '{nome}' já declarada", linha)
    else:
        tabela_variaveis[nome] = Simbolo(nome, tipo, _next_desloc)
        _next_desloc += 1

def busca_variavel(nome: str, linha: int):
    if nome not in tabela_variaveis:
        erro_semantico(f"variável '{nome}' não declarada", linha)
        return None
    return tabela_variaveis[nome]

# precedence (mesmo que seu parser original)
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'IGUAL', 'DIFERENTE', 'MENORQUE', 'MENORIGUAL', 'MAIORQUE', 'MAIORIGUAL'),
    ('left', 'MAIS', 'MENOS'),
    ('left', 'VEZES', 'DIV'),
    ('right', 'NOT', 'UMINUS'),
)

# ---------------------------
# Funções utilitárias de inferência de tipo a partir de AST
# (usamos para manter semântica dentro do parser, porém retornando AST)
# ---------------------------
def infer_tipo_expr(expr, linha):
    """
    Recebe um nó AST de expressão e tenta inferir/validar tipos,
    emitindo erros via erro_semantico(linha).
    Retorna 'integer' | 'boolean' | None
    """
    # Constantes
    if isinstance(expr, ast.CalcConstNum):
        expr.tipo = "integer"
        return "integer"
    if isinstance(expr, ast.CalcConstBool):
        expr.tipo = "boolean"
        return "boolean"
    if isinstance(expr, ast.CalcId):
        simbolo = busca_variavel(expr.nome, linha)
        if simbolo is None:
            expr.tipo = None
            return None
        expr.simbolo = simbolo
        expr.tipo = simbolo.tipo
        return simbolo.tipo
    if isinstance(expr, ast.CalculoUnario):
        t = infer_tipo_expr(expr.operand, linha)
        if expr.op == 'not':
            if t != "boolean":
                erro_semantico(f"operador 'not' requer expressão booleana (obtido {t})", linha)
            expr.tipo = "boolean"
            return "boolean"
        elif expr.op == '-':
            if t != "integer":
                erro_semantico(f"operador unário '-' requer expressão inteira (obtido {t})", linha)
            expr.tipo = "integer"
            return "integer"
        else:
            erro_semantico(f"operador unário desconhecido '{expr.op}'", linha)
            return None
    if isinstance(expr, ast.CalculoBinario):
        lt = infer_tipo_expr(expr.left, linha)
        rt = infer_tipo_expr(expr.right, linha)
        op = expr.op
        if op in ('+', '-', '*', '/', 'div', 'MAIS', 'MENOS', 'VEZES', 'DIV'):
            if lt != "integer" or rt != "integer":
                erro_semantico(f"operador '{op}' requer operandos inteiros (obtido {lt} e {rt})", linha)
            expr.tipo = "integer"
            return "integer"
        if op in ('and', 'or', 'AND', 'OR'):
            if lt != "boolean" or rt != "boolean":
                erro_semantico(f"operador '{op}' requer operandos booleanos (obtido {lt} e {rt})", linha)
            expr.tipo = "boolean"
            return "boolean"
        if op in ('=', '<>', 'IGUAL', 'DIFERENTE'):
            if lt != rt:
                erro_semantico(f"operador '{op}' requer operandos do mesmo tipo (obtido {lt} e {rt})", linha)
            expr.tipo = "boolean"
            return "boolean"
        if op in ('<', '<=', '>', '>=', 'MENORQUE', 'MENORIGUAL', 'MAIORQUE', 'MAIORIGUAL'):
            if lt != "integer" or rt != "integer":
                erro_semantico(f"operador '{op}' requer operandos inteiros (obtido {lt} e {rt})", linha)
            expr.tipo = "boolean"
            return "boolean"
        # fallback
        erro_semantico(f"operador binário desconhecido '{op}'", linha)
        return None
    # unknown
    return None

# ---------------------------
# Regras do parser — mantêm as checagens semânticas originais
# e também constroem e retornam nós AST (estilo parser_cldin2)
# ---------------------------

def p_programa(p):
    """programa : PROGRAM ID PV bloco PF"""
    instala_programa(p[2], p.lineno(2))
    # bloco já é um BlocoCmds
    prog = ast.Programa(bloco=p[4], nome=p[2])
    # anotar total_vars a partir da tabela_variaveis
    prog.total_vars = len(tabela_variaveis)
    p[0] = prog

def p_bloco(p):
    """bloco : declaracoes comando_composto"""
    # comando_composto retorna BlocoCmds; declaracoes pode ter inserido Declaracao nodes into the block
    p[0] = p[2]

def p_declaracoes(p):
    """declaracoes : VAR declaracao_variaveis
                   | empty"""
    # declaracao_variaveis already handled installations and returns list of Declaracao nodes
    if len(p) == 3:
        # p[2] is list of Declaracao nodes
        # We will attach them by prepending into upcoming block when building bloco,
        # but simpler: return them to caller (we'll merge in comando_composto if needed)
        p[0] = p[2]
    else:
        p[0] = []

def p_declaracao_variaveis(p):
    """declaracao_variaveis : lista_id DP tipo PV declaracao_variaveis
                            | lista_id DP tipo PV"""
    ids = p[1]
    tipo = p[3]
    linha = p.lineno(1)
    # instala cada variável (mantendo semântica)
    for nome in ids:
        instala_variavel(nome, tipo, linha)
    # criar nó Declaracao
    decl = ast.Declaracao(ids=ids, tipo=tipo)
    if len(p) == 6:
        # há sequência
        rest = p[5]  # lista de Declaracao
        p[0] = [decl] + rest
    else:
        p[0] = [decl]

def p_lista_id(p):
    """lista_id : ID
                | ID VIRG lista_id"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_tipo(p):
    """tipo : INTEGER
            | BOOLEAN"""
    p[0] = p[1].lower()

def p_comando_composto(p):
    """comando_composto : BEGIN lista_comandos END"""
    # lista_comandos returns a BlocoCmds
    p[0] = p[2]

def p_lista_comandos(p):
    """lista_comandos : comando
                      | comando PV lista_comandos
                      | comando PV"""
    if len(p) == 2:
        # single command: create block with it (unless it's None)
        if p[1] is None:
            p[0] = ast.BlocoCmds(lista_cmds=[])
        elif isinstance(p[1], ast.BlocoCmds):
            p[0] = p[1]
        else:
            p[0] = ast.BlocoCmds(lista_cmds=[p[1]])
    elif len(p) == 4:
        # comando PV lista_comandos
        left = [] if p[1] is None else ([p[1]] if not isinstance(p[1], ast.BlocoCmds) else p[1].lista_cmds)
        right = p[3].lista_cmds if isinstance(p[3], ast.BlocoCmds) else []
        p[0] = ast.BlocoCmds(lista_cmds=left + right)
    else:
        # comando PV (trailing)
        p[0] = ast.BlocoCmds(lista_cmds=[p[1]] if p[1] is not None else [])

def p_comando(p):
    """comando : atribuicao
               | comando_condicional
               | comando_enquanto
               | comando_leitura
               | comando_escrita
               | comando_composto
               | empty"""
    p[0] = p[1]

def p_atribuicao(p):
    """atribuicao : ID DPIGUAL expressao"""
    linha = p.lineno(1)
    # semântica: verificar variável
    tipo_var = busca_variavel(p[1], linha)
    expr_node = p[3]
    # inferir tipo da expressão (faz verificações internas)
    tipo_expr = infer_tipo_expr(expr_node, linha)
    if tipo_var and tipo_expr and tipo_var.tipo != tipo_expr:
        erro_semantico(f"atribuição incompatível: variável '{p[1]}' é {tipo_var.tipo}, expressão é {tipo_expr}", linha)
    # construir AST (CalcId com simbolo se disponível)
    calc_id = ast.CalcId(nome=p[1])
    if tipo_var:
        calc_id.simbolo = tipo_var
        calc_id.tipo = tipo_var.tipo
    p[0] = ast.Atribuicao(id=calc_id, expr=expr_node)

def p_comando_condicional(p):
    """comando_condicional : IF expressao THEN comando
                           | IF expressao THEN comando ELSE comando"""
    linha = p.lineno(1)
    expr_node = p[2]
    tipo_cond = infer_tipo_expr(expr_node, linha)
    if tipo_cond != "boolean":
        erro_semantico("condição do IF deve ser booleana", linha)
    # construir nós then/else: p[4] e possivelmente p[6]
    then_node = (
        p[4] if isinstance(p[4], ast.BlocoCmds)
        else ast.BlocoCmds(lista_cmds=[p[4]]) if p[4]
        else ast.BlocoCmds([])
    )

    if len(p) == 5:
        # IF expr THEN comando   ✅ SEM ELSE
        p[0] = ast.Condicional(cond=expr_node, then_cmd=then_node, else_cmd=None)
    else:
        # IF expr THEN comando ELSE comando ✅ COM ELSE
        else_node = (
            p[6] if isinstance(p[6], ast.BlocoCmds)
            else ast.BlocoCmds(lista_cmds=[p[6]]) if p[6]
            else ast.BlocoCmds([])
        )
        p[0] = ast.Condicional(cond=expr_node, then_cmd=then_node, else_cmd=else_node)

def p_comando_enquanto(p):
    """comando_enquanto : WHILE expressao DO comando"""
    linha = p.lineno(1)
    expr_node = p[2]
    tipo_cond = infer_tipo_expr(expr_node, linha)
    if tipo_cond != "boolean":
        erro_semantico("condição do WHILE deve ser booleana", linha)
    bloco = p[4] if isinstance(p[4], ast.BlocoCmds) else ast.BlocoCmds(lista_cmds=[p[4]]) if p[4] else ast.BlocoCmds([])
    p[0] = ast.Enquanto(cond=expr_node, bloco=bloco)

def p_comando_leitura(p):
    """comando_leitura : READ EPAR lista_id DPAR"""
    linha = p.lineno(1)
    # verificar variáveis existem e construir CalcId list
    calc_ids = []
    for nome in p[3]:
        simb = busca_variavel(nome, linha)
        if simb is None:
            # busca_variavel já emite erro
            calc_ids.append(ast.CalcId(nome=nome))
        else:
            cid = ast.CalcId(nome=nome)
            cid.simbolo = simb
            cid.tipo = simb.tipo
            calc_ids.append(cid)
    p[0] = ast.Leitura(ids=calc_ids)

def p_comando_escrita(p):
    """comando_escrita : WRITE EPAR lista_expressoes DPAR"""
    linha = p.lineno(1)
    # validar tipos das expressões
    for e in p[3]:
        t = infer_tipo_expr(e, linha)
        if t not in ("integer", "boolean"):
            erro_semantico(f"write() recebeu tipo inválido '{t}'", linha)
    p[0] = ast.Escrita(exprs=p[3])

def p_lista_expressoes(p):
    """lista_expressoes : expressao
                        | expressao VIRG lista_expressoes"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

# ---------------------------
# EXPRESSÕES: agora retornam nós AST (e depois inferimos tipos)
# ---------------------------

def p_expressao_or(p):
    """expressao : expressao OR expressao_and
                 | expressao_and"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ast.CalculoBinario(left=p[1], op='or', right=p[3])

def p_expressao_and(p):
    """expressao_and : expressao_and AND expressao_rel
                      | expressao_rel"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ast.CalculoBinario(left=p[1], op='and', right=p[3])

def p_expressao_rel(p):
    """expressao_rel : soma relacao soma
                     | soma"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ast.CalculoBinario(left=p[1], op=p[2], right=p[3])

def p_soma(p):
    """soma : soma MAIS termo
            | soma MENOS termo
            | termo"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ast.CalculoBinario(left=p[1], op=p[2], right=p[3])

def p_termo(p):
    """termo : termo VEZES fator
             | termo DIV fator
             | fator"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ast.CalculoBinario(left=p[1], op=p[2], right=p[3])

def p_fator(p):
    """fator : ID
             | NUMERO
             | TRUE
             | FALSE
             | EPAR expressao DPAR
             | NOT fator
             | MENOS fator %prec UMINUS"""
    if len(p) == 2:
        tok = p.slice[1].type
        if tok == "NUMERO":
            p[0] = ast.CalcConstNum(valor=p[1])
        elif tok in ("TRUE", "FALSE"):
            val = True if str(p[1]).lower() == 'true' else False
            p[0] = ast.CalcConstBool(valor=val)
        elif tok == "ID":
            p[0] = ast.CalcId(nome=p[1])
        else:
            p[0] = ast.CalcConstNum(valor=0)  # fallback
    elif len(p) == 4 and p.slice[1].type == "EPAR":
        p[0] = p[2]
    elif p.slice[1].type == "NOT":
        p[0] = ast.CalculoUnario(op='not', operand=p[2])
    elif p.slice[1].type == "MENOS":
        p[0] = ast.CalculoUnario(op='-', operand=p[2])

def p_relacao(p):
    """relacao : IGUAL
               | DIFERENTE
               | MENORQUE
               | MENORIGUAL
               | MAIORQUE
               | MAIORIGUAL"""
    p[0] = p[1]

def p_empty(p):
    """empty :"""
    p[0] = None

def p_error(p):
    if p:
        msg = f"ERRO SINTÁTICO: token inesperado '{p.value}' na linha {p.lineno}"
    else:
        msg = "ERRO SINTÁTICO: fim de arquivo inesperado."
    
    print(msg)
    erros_sintaticos.append(msg)

# construir parser
parser = yacc.yacc()