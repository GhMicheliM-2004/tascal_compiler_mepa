# 🖥️ Tascal Compiler → MEPA

Este projeto implementa um **compilador completo para a linguagem Tascal**, desenvolvido como trabalho acadêmico, que realiza todas as etapas clássicas de um compilador:

- ✅ Análise Léxica  
- ✅ Análise Sintática  
- ✅ Análise Semântica  
- ✅ Construção de AST (Árvore Sintática Abstrata)  
- ✅ Geração de Código Intermediário para a Máquina Virtual **MEPA**  
- ✅ Execução do código MEPA via interpretador  

O objetivo principal do trabalho é **traduzir programas escritos em Tascal para código MEPA executável**, validando corretamente todos os erros da linguagem antes da geração do código.

---

## 🎯 Objetivo do Sistema

O sistema recebe como entrada um arquivo:

programa.tascal

E produz como saída:

programa.mepacal

Esse código gerado pode ser executado diretamente em uma **Máquina Virtual MEPA**, permitindo validar completamente o funcionamento do compilador.

Além disso, o sistema:

- Detecta **erros léxicos**
- Detecta **erros sintáticos**
- Detecta **erros semânticos**
- **Só gera código MEPA se NÃO houver nenhum erro**

---

## ⚙️ Etapas do Compilador

### 1️⃣ Análise Léxica (Lexer)
Arquivo responsável:

lexer_tascal_mepa.py

Função:
- Reconhece os tokens da linguagem:
  - Palavras-chave (`program`, `var`, `begin`, `end`, `if`, `while`, `read`, `write`, etc.)
  - Identificadores
  - Números
  - Operadores (`+ - * div = <> < <= > >= and or not`)
- Detecta **erros léxicos**, como símbolos inválidos.

---

### 2️⃣ Análise Sintática + Semântica (Parser)
Arquivo responsável:

parser_tascal_mepa.py

Função:
- Valida a **estrutura gramatical do programa**.
- Garante que:
  - Variáveis são declaradas antes de serem usadas
  - Tipos são compatíveis nas atribuições
  - Expressões lógicas usam booleanos
  - Expressões aritméticas usam inteiros
- Constrói a **AST (Árvore Sintática Abstrata)**.

Se houver qualquer erro:
- ❌ A compilação é interrompida
- ❌ O código MEPA NÃO é gerado

---

### 3️⃣ AST – Árvore Sintática Abstrata
Arquivo:

ast_tascal_mepa.py

Função:
- Representa o programa em forma de árvore
- Cada comando vira um nó:
  - `Atribuicao`
  - `Condicional`
  - `Enquanto`
  - `Leitura`
  - `Escrita`
  - `CalculoBinario`
  - `CalculoUnario`
  - `CalcId`
  - `CalcConstNum`
  - `CalcConstBool`

Essa AST é usada diretamente pelo **gerador MEPA**.

---

### 4️⃣ Geração de Código MEPA
Arquivo:

mepa_tascal.py

Função:
- Percorre a AST
- Converte cada nó em instruções da máquina MEPA:
  - `INPP` → início do programa
  - `AMEM` → alocação de memória
  - `CRCT` → carregar constante
  - `CRVL` → carregar variável
  - `ARMZ` → armazenar valor
  - `SOMA`, `SUBT`, `MULT`, `DIVI` → operações
  - `DSVF`, `DSVS` → desvios (if / while)
  - `IMPR` → impressão
  - `PARA`, `FIM` → finalização

---

### 5️⃣ Arquivo Principal (Execução da Compilação)
Arquivo:

main.py

Função:
- Lê o arquivo `.tascal`
- Executa:
  1. Lexer
  2. Parser
  3. Análise Semântica
- Se houver erro:

COMPILAÇÃO FINALIZADA COM ERROS — GERAÇÃO MEPA CANCELADA.

- Se estiver tudo certo:
- Gera o arquivo `.mepacal`
- Exibe o código MEPA no terminal

---

## ▶️ Como Compilar um Programa Tascal

No terminal, execute:

py main.py testes_Tascal_disponibilizado/P01.tascal

Se estiver tudo correto:

✅ Código MEPA será exibido  
✅ Um arquivo `.mepacal` será gerado automaticamente  

Exemplo:

P01.mepacal

---

## ▶️ Como Executar o Código MEPA

Entre na pasta `mepa`:

cd mepa

Execute:

py mepa_pt.py --progfile ..testes/arquivos_mepacal/P01.mepacal

Isso executa o código gerado pelo compilador.

---

## ✅ Características Implementadas

- ✔️ Declaração de variáveis inteiras e booleanas
- ✔️ Leitura (`read`)
- ✔️ Escrita (`write`)
- ✔️ Atribuições (`:=`)
- ✔️ Condicionais (`if` / `else`)
- ✔️ Laço de repetição (`while`)
- ✔️ Operadores aritméticos (`+ - * div`)
- ✔️ Operadores relacionais
- ✔️ Operadores lógicos (`and`, `or`, `not`)
- ✔️ Geração real de código MEPA executável

---

## 👨‍🎓 Autor

Projeto desenvolvido como trabalho prático da disciplina de **Compiladores**.

Autor: **Gustavo Michelim**,**Leonardo Almenara**

Curso: **Engenharia de Software**

---

## ✅ Conclusão

Este sistema implementa um **compilador completo**, indo desde a leitura do código-fonte em Tascal até a execução final na **Máquina Virtual MEPA**, respeitando todas as etapas formais exigidas em um projeto de compiladores.

O projeto está totalmente funcional, validado por diversos testes e pronto para avaliação acadêmica.

