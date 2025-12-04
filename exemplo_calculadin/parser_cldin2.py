import ply.yacc as yacc
from lexer_cldin2  import tokens, make_lexer
import ast_cldin2 as ast
import sys

parser = None

precedence = (
    ('nonassoc', 'IFS'),
    ('nonassoc', 'ELSE'),
    ('right', 'NOT')
)

def p_programa(p):
    "programa : INICIAR CALCULADIN ':' cmds FINALIZAR CALCULADIN PT"
    p[0] = ast.Programa(bloco_cmds=p[4])

def p_cmds_lista(p):
    "cmds : cmds cmd"
    p[1].lista_cmds.append(p[2])
    p[0] = p[1]
    
def p_cmds_vazio(p):
    "cmds : "
    p[0] = ast.BlocoCmds(lista_cmds=[])

def p_cmd_tipos(p):
    """cmd : funcao
           | atribuicao
           | declaracao
           | condicional"""
    p[0] = p[1]

def p_declaracao(p):
    "declaracao : tipo ID ';'"
    p[0] = ast.Declaracao(nome_tipo=p[1], id=ast.CalcId(nome=p[2]))

def p_tipo_real(p):
    """tipo : REAL
            | BOOL"""
    p[0] = p[1]

def p_condicional_simples(p):
    """condicional : IF '(' calculo ')' '{' cmds '}' %prec IFS"""
    p[0] = ast.Condicional(condicao=p[3], bloco_then=p[6], bloco_else=None)

def p_condicional_else(p):
    """condicional : IF '(' calculo ')' '{' cmds '}' ELSE '{' cmds '}'"""
    p[0] = ast.Condicional(condicao=p[3], bloco_then=p[6], bloco_else=p[10])

def p_funcao(p):
    """funcao : INPUT '(' ID ')' ';'
              | OUTPUT '(' ID ')' ';'"""
    p[0] = ast.Funcao(nome_funcao=p[1], argumento=ast.CalcId(nome=p[3]))

def p_atribuicao(p):
    "atribuicao : ID ATRIB calculo ';'"
    p[0] = ast.Atribuicao(id=ast.CalcId(nome=p[1]), calculo=p[3])

def p_calculo(p):
    "calculo : expr"
    p[0] = p[1]

def p_calculo_relacao(p):
    "calculo : expr relacao expr"
    p[0] = ast.CalculoBinario(esq=p[1], op=p[2], dir=p[3])

def p_relacao(p):
    """relacao : IGUAL
               | DIFERENTE
               | MENOR
               | MENOR_IGUAL
               | MAIOR
               | MAIOR_IGUAL"""
    p[0] = p[1]

def p_expr_termo(p):
    "expr : termo"
    p[0] = p[1]

def p_expr_binaria(p):
    """expr : expr '+' termo
            | expr '-' termo
            | expr OR termo"""
    p[0] = ast.CalculoBinario(esq=p[1], op=p[2], dir=p[3])

def p_termo_fator(p):
    "termo : fator"
    p[0] = p[1]

def p_termo_binario(p):
    """termo : termo '*' fator
             | termo '/' fator
             | termo AND fator"""
    p[0] = ast.CalculoBinario(esq=p[1], op=p[2], dir=p[3])

def p_fator_id(p):
    """fator : ID"""
    p[0] = ast.CalcId(nome=p[1])

def p_fator_num(p):
    """fator : NUM"""
    p[0] = ast.CalcConstNum(valor=p[1])

def p_fator_logico(p):
    """fator : TRUE
             | FALSE"""
    p[0] = ast.CalcConstBool(valor=(p[1] == 'true'))

def p_fator_paren(p):
    "fator : '(' calculo ')'"
    p[0] = p[2]

def p_fator_unario(p):
    """fator : NOT fator"""
    p[0] = ast.CalculoUnario(op=p[1], calculo=p[2])

def p_error(p):
    global parser
    if p:
        print(f"Erro sintático: Token inesperado: {p.type} ('{p.value}') na linha {p.lineno}", file=sys.stderr)
    else:
        print("Erro sintático: Fim inesperado do arquivo (EOF).", file=sys.stderr)
    parser.tem_erro = True

def make_parser():
    global parser
    parser = yacc.yacc()
    parser.tem_erro = False
    return parser