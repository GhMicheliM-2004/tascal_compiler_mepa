
# Analisador léxico para a linguagem Tascal usando PLY
import ply.lex as lex

erros_lexicos = []  # Lista para armazenar erros léxicos

palavras_reservadas = { # Palavras reservadas do Tascal
    'program': 'PROGRAM',
    'var': 'VAR',
    'begin': 'BEGIN',
    'end': 'END',
    'integer': 'INTEGER',
    'boolean': 'BOOLEAN',
    'false': 'FALSE',
    'true': 'TRUE',
    'read': 'READ',
    'write': 'WRITE',
    'while': 'WHILE',
    'do': 'DO',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'div': 'DIV',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
}
 
tokens = [ # Definição dos tokens
    'ID', 'NUMERO',
    'EPAR', 'DPAR', 'PV',
    'IGUAL', 'DIFERENTE',
    'MENORQUE', 'MENORIGUAL',
    'MAIORQUE', 'MAIORIGUAL',
    'MAIS', 'MENOS', 'VEZES',
    'DPIGUAL', 'DP', 'VIRG', 'PF'
] + list(palavras_reservadas.values())

# Definição das expressões regulares para os tokens simples
t_EPAR = r'\(' 
t_DPAR = r'\)'
t_PV = r';'
t_IGUAL = r'='
t_DIFERENTE = r'<>'
t_MENORIGUAL = r'<='
t_MAIORIGUAL = r'>='
t_MENORQUE = r'<'
t_MAIORQUE = r'>'
t_MAIS = r'\+'
t_MENOS = r'-'
t_VEZES = r'\*'
t_DPIGUAL = r':='
t_DP = r':'
t_VIRG = r','
t_PF = r'\.'
t_ignore = ' \t'

def t_ID(t): # Identificador
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = palavras_reservadas.get(t.value, 'ID')
    return t

def t_NUMERO(t): # Número inteiro
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t): # Quebra de linha
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_COMMENT(t): # Comentários -> Não são permitidos
    r'\{[^}]*\}'
    msg = f"ERRO LÉXICO: Comentários não são permitidos (linha {t.lineno})"
    print(msg)
    erros_lexicos.append(msg)

def t_error(t): # Tratamento de erros léxicos
    msg = f"ERRO LÉXICO: Símbolo ilegal '{t.value[0]}' na linha {t.lineno}"
    print(msg)
    erros_lexicos.append(msg)
    t.lexer.skip(1)

# Construção do analisador léxico
lexico = lex.lex()
