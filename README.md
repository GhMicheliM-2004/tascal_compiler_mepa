# Tascal Compiler → MEPA

Compilador para a linguagem **Tascal**, que realiza análise léxica, sintática, semântica e gera código intermediário para a máquina virtual **MEPA**.  

---

## ✨ Visão Geral

Este projeto implementa um compilador completo para a linguagem Tascal, suportando:

- Analisador léxico (lexer)  
- Analisador sintático + semântico (parser + checagem de tipos, declaração/uso de variáveis)  
- Construção de AST (árvore sintática abstrata)  
- Geração de código intermediário para a máquina MEPA (instruções como `INPP`, `AMEM`, `CRCT`, `CRVL`, `ARMZ`, `SOMA`, `SUBT`, `MULT`, `DIVI`, `DSVF`, `DSVS`, `IMPR`, `PARA`, `FIM`, etc.)  

O compilador transforma um programa .tas escrito em Tascal em um programa MEPA pronto para execução pela máquina virtual MEPA.

---

## 📁 Estrutura do repositório
