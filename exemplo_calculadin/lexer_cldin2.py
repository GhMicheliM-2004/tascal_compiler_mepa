import ply.lex as lex

reservadas = {
    'iniciar':    'INICIAR',
    'calculadin': 'CALCULADIN',
    'finalizar':  'FINALIZAR',
    'real':       'REAL',
    'bool':       'BOOL',
    'if':         'IF',
    'else':       'ELSE',
    'input':      'INPUT',
    'output':     'OUTPUT',
    'or':         'OR',
    'and':        'AND',
    'not':        'NOT',
    'true':       'TRUE',
    'false':      'FALSE',
}

tokens = [
    'ID',
    'NUM',
    'ATRIB',       # =
    'IGUAL',       # ==
    'DIFERENTE',   # !=
    'MENOR_IGUAL', # <=
    'MAIOR_IGUAL', # >=
    'MENOR',       # <
    'MAIOR',       # >
    'PT',          # .

] + list(reservadas.values())


literals = [
    ':', ';', '(', ')', '{', '}',
    '+', '-', '*', '/',
]

# Tokens de operadores (ordem importa)
t_IGUAL       = r'=='
t_DIFERENTE   = r'!='
t_MENOR_IGUAL = r'<='
t_MAIOR_IGUAL = r'>='
t_ATRIB       = r'='
t_MENOR       = r'<'
t_MAIOR       = r'>'

def t_PT(t):
    r'\.'
    t.type = 'PT'
    return t

def t_NUM(t):
    r'\d+(\.\d*)?'
    t.value = float(t.value)
    return t

def t_ID(t):
    r'[a-z][a-z0-9]*'
    t.type = reservadas.get(t.value, 'ID')
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Erro léxico: Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.tem_erro = True
    t.lexer.skip(1)

def make_lexer():
    lexer = lex.lex()
    lexer.tem_erro = False
    return lexer

if __name__ == '__main__':
    pass