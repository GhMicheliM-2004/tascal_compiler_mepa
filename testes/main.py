# Arquivo testador do programa
# Permite realizar a verificação se houve erros nas análises e chamar a criação de código mepa
import sys
from lexer_tascal_mepa import lexico, erros_lexicos
from parser_tascal_mepa import parser, semantico_reset, erros_semanticos, erros_sintaticos
from mepa_tascal import GeradorMEPA

arquivo_entrada = sys.argv[1]

# Leitura do arquivo
try:
    with open(arquivo_entrada, "r", encoding="utf-8") as f:
        codigo_fonte = f.read()
except FileNotFoundError:
    print(f"Erro: Arquivo '{arquivo_entrada}' não encontrado.")
    sys.exit(1)

# Reset geral de erros
semantico_reset()
erros_lexicos.clear()
erros_semanticos.clear()
erros_sintaticos.clear()

# Garantindo análise sintático (erro de bloqueio)
ast = parser.parse(codigo_fonte, lexer=lexico)

if ast is None:
    print("\nCOMPILAÇÃO FINALIZADA COM ERROS — GERAÇÃO MEPA CANCELADA")
    sys.exit(1)

# Relatório final de erros, verificando se tem erros nas análises sintática, semântica e léxica
houve_erros = False

if erros_lexicos:
    houve_erros = True
    
if erros_sintaticos:
    houve_erros = True

if erros_semanticos:
    houve_erros = True

# Se possuir erros, bloqueia a geração de código mepa
if houve_erros:
    print("\nCOMPILAÇÃO FINALIZADA COM ERROS — GERAÇÃO MEPA CANCELADA.")
    sys.exit(1)

# Senão, continua executando a geraçãode código
print("\nANÁLISE LÉXICA, SINTÁTICA E SEMÂNTICA OK!")

# Gerando código mepa
gerador = GeradorMEPA()
codigo_mepa = gerador.gera(ast)

print("\nCÓDIGO MEPA GERADO:\n")
for linha in codigo_mepa:
    print(linha)

# Salvamos em arquivo .mepacal (pasta arquivos_mepacal)
arquivo_saida = arquivo_entrada.replace(".tas", ".mepa")

with open(arquivo_saida, "w", encoding="utf-8") as f:
    for linha in codigo_mepa:
        f.write(linha + "\n")

print(f"\nArquivo '{arquivo_saida}' gerado com sucesso!")
