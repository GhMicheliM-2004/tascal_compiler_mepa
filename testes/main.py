import sys
from lexer_tascal_mepa import lexico, erros_lexicos
from parser_tascal_mepa import parser, semantico_reset, erros_semanticos, erros_sintaticos
from mepa_tascal import GeradorMEPA

# -------------------------------
# VERIFICA ARGUMENTO
# -------------------------------
if len(sys.argv) != 2:
    print("Uso correto:")
    print("   python main.py arquivo.tas")
    sys.exit(1)

arquivo_entrada = sys.argv[1]

# -------------------------------
# LEITURA DO ARQUIVO
# -------------------------------
try:
    with open(arquivo_entrada, "r", encoding="utf-8") as f:
        codigo_fonte = f.read()
except FileNotFoundError:
    print(f"Erro: Arquivo '{arquivo_entrada}' não encontrado.")
    sys.exit(1)

# -------------------------------
# RESET GERAL DE ERROS
# -------------------------------
semantico_reset()
erros_lexicos.clear()
erros_semanticos.clear()
erros_sintaticos.clear()

# -------------------------------
# ANÁLISE LÉXICA + SINTÁTICA + SEMÂNTICA
# -------------------------------
ast = parser.parse(codigo_fonte, lexer=lexico)

# SE O PARSER FALHOU COMPLETAMENTE (ERRO SINTÁTICO GRAVE)
if ast is None:
    print("\n❌ COMPILAÇÃO FINALIZADA COM ERROS SINTÁTICOS — GERAÇÃO MEPA CANCELADA.")
    sys.exit(1)

# -------------------------------
# RELATÓRIO FINAL DE ERROS
# -------------------------------
houve_erros = False

if erros_lexicos:
    houve_erros = True
    
if erros_sintaticos:
    houve_erros = True

if erros_semanticos:
    houve_erros = True

# -------------------------------
# BLOQUEIO TOTAL DO MEPA SE HOUVER ERRO
# -------------------------------
if houve_erros:
    print("\n❌ COMPILAÇÃO FINALIZADA COM ERROS — GERAÇÃO MEPA CANCELADA.")
    sys.exit(1)

print("\n✅ ANÁLISE LÉXICA, SINTÁTICA E SEMÂNTICA OK!")

# -------------------------------
# GERAÇÃO DE CÓDIGO MEPA
# -------------------------------
gerador = GeradorMEPA()
codigo_mepa = gerador.gera(ast)

print("\n📌 CÓDIGO MEPA GERADO:\n")
for linha in codigo_mepa:
    print(linha)

# -------------------------------
# SALVA ARQUIVO .mepa
# -------------------------------
arquivo_saida = arquivo_entrada.replace(".tas", ".mepa")

with open(arquivo_saida, "w", encoding="utf-8") as f:
    for linha in codigo_mepa:
        f.write(linha + "\n")

print(f"\n✅ Arquivo '{arquivo_saida}' gerado com sucesso!")
