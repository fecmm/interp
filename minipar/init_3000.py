import sys
from typing import List, Optional, Dict, Any
from lexer_251018_215612 import Lexer, Token, LexerError
from parser_251018_215706 import Parser, ParserError
from ast_251018_215806 import Program, AST, Block, VarRef, BinaryOp, IfStmt, WhileStmt, FuncDecl, VarDecl, Literal, Call, VarAssign, VarDeclStmt, PrintStmt, Stmt
from semantic_3000 import SemanticAnalyzer, SemanticError, ASTVisitor
from interpreter_3000 import Interpreter, RuntimeError, ReturnException, BreakException


def print_section_header(title):
    print("\n")
    print(f" {title.center(46)} ")
    print("\n")

def main():
    if len(sys.argv) < 2:
        print("Uso: python init.py <arquivo.minipar>")
        sys.exit(1)
    input_file = sys.argv[1]
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            code = f.read()
        #1: Analise lexica
        print_section_header("1: Análise Léxica (Tokens gerados):")
        lexer = Lexer(code)
        tokens: List[Token] = lexer.tokenize()
        for token in tokens:
            print(f"Token(type='{token.type.ljust(10)}', value='{token.value.replace('\n', '\\n')}', line={token.line}, col={token.col})")
        print(f"Total de tokens: {len(tokens)}")
        #2: Analise sintatica (AST)
        print_section_header("2: Análise Sintática (AST):")
        parser = Parser(tokens)
        program_ast: Program = parser.parse_program()
        print(program_ast)
        print("---Estrutura do Programa:")
        print(f"Classes Declaradas ({len(program_ast.classes)}):")
        for cls in program_ast.classes:
            print(f"  - {cls.name} (Base: {cls.base})")
            for field in cls.fields:
                 print(f"    -> Field: {field.name}: {field.type_name}")
            for method in cls.methods:
                 print(f"    -> Method: {method.name}(...) -> {method.ret_type}")
        print(f"Instruções/Comandos ({len(program_ast.stmts)}):")
        for stmt in program_ast.stmts:
             print(f"  - {stmt.__class__.__name__}")
        #3: Anaçise semantica
        print_section_header("3: Análise Semântica: ")
        analyzer = SemanticAnalyzer()
        validated_ast = analyzer.analyze(program_ast)
        print("Escopo e Tipos validados:")
        print(validated_ast) #print da AST validade pela analise semantica
        #AST: Arvore sintática Abstrata, arvore de derivação
        #4: Iinterpretador
        print_section_header("4: Interpretador: ")
        interpreter = Interpreter()
        interpreter.interpret(validated_ast)
        print("\nExecução finalizada com sucesso")

#tratamento de possíveis erros:
    except FileNotFoundError:
        print(f"Erro: O arquivo '{input_file}' não foi encontrado.")
        sys.exit(1)
    except LexerError as e:
        print("\n" + "-"*50)
        print(f"Erro de Análise Léxica: {e}")
        sys.exit(1)
    except ParserError as e:
        print("\n" + "-"*50)
        print(f"Erro de Análise Sintática: {e}")
        sys.exit(1)
    except SemanticError as e:
        print("\n" + "-"*50)
        print(f"Erro de Análise Semântica: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print("\n" + "-"*50)
        print(f"Erro em Tempo de Execução: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":

    main()

