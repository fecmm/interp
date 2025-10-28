from typing import List
from lexer_251018_215612 import Token, Lexer
from ast_251018_215806 import *

class ParserError(Exception): pass
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def next(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, ttype):
        tok = self.peek()
        if tok.type != ttype:
            raise ParserError(f"Expected {ttype} but got {tok.type} at {tok.line}:{tok.col}")
        return self.next()

    def parse_program(self) -> Program:
        classes = []
        stmts = []
        while self.peek().type != "EOF":
            if self.peek().type == "CLASS": 
                classes.append(self.parse_class())
            elif self.peek().type == "FUNC":
                stmts.append(self.parse_stmt())
            else:
                stmts.append(self.parse_stmt())
        return Program(classes=classes, stmts=stmts)

    def parse_class(self) -> ClassDecl:
        self.expect("CLASS") 
        name = self.expect("ID").value
        base = None
        if self.peek().type == "EXTENDS": 
            self.next()
            base = self.expect("ID").value
        self.expect("{")
        fields = []
        methods = []
        while self.peek().type != "}":
            if self.peek().type == "VAR": 
                fields.append(self.parse_var_decl(require_semicolon=False)) 
            elif self.peek().type == "FUNC": 
                methods.append(self.parse_func_decl())
            else:
                raise ParserError(f"Unexpected token in class body: {self.peek().type}")
        self.expect("}")
        return ClassDecl(name, base, fields, methods)

    # def parse_var_decl(self, require_semicolon=False) -> VarDecl:
    def parse_var_decl(self) -> VarDecl: #retirei um parametro que nao estava sendo usada, se der algum problema pode ser aqui
        if self.peek().type == "VAR":
            self.expect("VAR")
        name = self.expect("ID").value
        self.expect(":")
        type_tok = self.next()
        if type_tok.type not in ("ID", "NUMBER", "INT", "BOOL", "STRING", "C_CHANNEL"):
             raise ParserError(f"Expected type identifier but got {type_tok.type}")
        type_name = type_tok.value
        init = None
        if self.peek().type == "=":
            self.next()
            init = self.parse_expression()
        return VarDecl(name, type_name, init)

    def expect_symbol(self, expected_value: str, error_message: str = ""):
            tok = self.expect("OP")
            if tok.value != expected_value:
                msg = error_message if error_message else f"Expected '{expected_value}' but got '{tok.value}'"
                raise ParserError(f"{msg} at {tok.line}:{tok.col}")
            return tok

    def parse_func_decl(self) -> FuncDecl:
        self.expect("FUNC") 
        name = self.expect("ID").value
        self.expect_symbol("(", "Erro na abertura de parâmetros") 
        params = []
        if self.peek().type == "OP" and self.peek().value == ")":
            self.next() 
        else:
            while True:
                p_name = self.expect("ID").value
                self.expect_symbol(":", "Erro no separador de tipo do parâmetro")
                p_type_tok = self.next()
                valid_types = ("ID", "NUMBER", "INT", "BOOL", "STRING", "C_CHANNEL")
                if p_type_tok.type not in valid_types:
                     raise ParserError(f"Expected a valid type name (ID, NUMBER, INT, etc.) but got {p_type_tok.type} ('{p_type_tok.value}') at {p_type_tok.line}:{p_type_tok.col}")
                p_type = p_type_tok.value
                params.append(VarDecl(p_name, p_type, None))
                if self.peek().type == "OP" and self.peek().value == ",":
                    self.next() 
                    continue
                else:
                    break
            self.expect_symbol(")", "Erro no fechamento de parâmetros")
        self.expect_symbol("->", "Erro no indicador de retorno")
        ret_type_tok = self.next()
        if ret_type_tok.type not in valid_types:
             raise ParserError(f"Expected a valid return type name but got {ret_type_tok.type} ('{ret_type_tok.value}') at {ret_type_tok.line}:{ret_type_tok.col}")
        ret_type = ret_type_tok.value
        body = self.parse_block()
        return FuncDecl(name, params, ret_type, body)

    def parse_block(self) -> Block:
        self.expect_symbol("{", "Esperado '{' para iniciar bloco")
        stmts = []
        while self.peek().type != "OP" or self.peek().value != "}":
            if self.peek().type == "EOF": 
                 raise ParserError("Bloco não fechado (EOF inesperado)")
            stmts.append(self.parse_stmt())
        self.expect_symbol("}", "Esperado '}' para fechar bloco")
        return Block(stmts)
    
    def parse_expression(self, rbp=0):
        tok = self.next()
        left = self.nud(tok)
        while rbp < self.lbp(self.peek()):
            tok = self.next()
            left = self.led(tok, left)
        return left 

    def nud(self, tok: Token): 
        if tok.type == "NUMBER": 
            return Literal(int(tok.value))
        if tok.type == "STRING": 
            return Literal(tok.value[1:-1])
        if tok.type == "TRUE": 
            return Literal(True)
        if tok.type == "FALSE": 
            return Literal(False)
        if tok.type == "OP" and tok.value == "(": 
            expr = self.parse_expression()
            self.expect_symbol(")", "Esperado ')' para fechar agrupamento")
            return expr
        if tok.type == "OP" and tok.value in ("-", "!"):
            right = self.parse_expression(70) 
            return UnaryOp(tok.value, right)
        if tok.type == "ID":
            if self.peek().type == "OP" and self.peek().value == "(": 
                self.next()
                args = []
                if self.peek().type != "OP" or self.peek().value != ")": 
                    while True:
                        args.append(self.parse_expression())
                        if self.peek().type == "OP" and self.peek().value == ",":
                            self.next()
                            continue
                        else:
                            break
                self.expect_symbol(")", "Esperado ')' para fechar argumentos da chamada de função")
                return Call(VarRef(tok.value), args)
            return VarRef(tok.value)
        if tok.type == "NEW": 
            class_name = self.expect("ID").value
            self.expect_symbol("(", "Esperado '(' para chamada do construtor")
            self.expect_symbol(")", "Esperado ')' para chamada do construtor")
            return NewObj(class_name)
        raise ParserError(f"Unexpected token {tok.type} ('{tok.value}') in expression at {tok.line}:{tok.col}. Expected: NUMBER, ID, TRUE, FALSE, NEW, (, ou operador unário.")

    def lbp(self, tok: Token):
        if tok.type == "OP":
            v = tok.value
            if v in ("||"): 
                return 10
            if v in ("&&"): 
                return 20
            if v in ("==", "!="): 
                return 30
            if v in ("<", ">", "<=", ">="): 
                return 40
            if v in ("+", "-"): 
                return 50
            if v in ("*", "/"): 
                return 60
        if tok.type == "(":
            return 80
        return 0

    def led(self, tok: Token, left):
        if tok.type == "OP":
            op = tok.value
            if op in ("+", "-", "*", "/", "==", "!=", "<", ">", "<=", ">=", "&&", "||"):
                right = self.parse_expression(self.lbp(tok))
                return BinaryOp(left, op, right)
        if tok.type == "(":
            args = []
            if self.peek().type != ")":
                while True:
                    args.append(self.parse_expression())
                    if self.peek().type == ",":
                        self.next()
                        continue
                    else: 
                        break
            self.expect(")") 
            return Call(left, args)
        raise ParserError("Unexpected operator")
    
    def parse_if(self) -> IfStmt:
        self.expect("IF")
        self.expect_symbol("(", "Esperado '(' para iniciar a condição do if")
        cond = self.parse_expression()
        self.expect_symbol(")", "Esperado ')' para fechar a condição do if")
        then_branch = self.parse_stmt()
        else_branch = None
        if self.peek().type == "ELSE":
            self.next()
            else_branch = self.parse_stmt()
        return IfStmt(cond, then_branch, else_branch)
    
    def parse_stmt(self) -> Stmt:
        tok = self.peek()
        if tok.type == "VAR":
            self.expect("VAR")
            decl = self.parse_var_decl_content()
            return VarDeclStmt(decl)
        if tok.type == "IF": 
            return self.parse_if() 
        if tok.type == "WHILE": 
            return self.parse_while()
        if tok.type == "SEQ": 
            self.next()
            return SeqBlock(self.parse_block())
        if tok.type == "PAR": 
            self.next()
            return ParBlock(self.parse_block())
        if tok.type == "SEND": 
            return self.parse_send()
        if tok.type == "RECEIVE": 
            return self.parse_receive()
        if tok.type == "PRINT": 
            self.next()
            self.expect_symbol("(", "Esperado '(' para iniciar a expressão do print")
            expr = self.parse_expression()
            self.expect_symbol(")", "Esperado ')' para fechar a expressão do print")
            return PrintStmt(expr)
        if tok.type == "BREAK": 
            self.next()
            return BreakStmt()
        if tok.type == "RETURN": 
            self.next()
            expr = None
            if self.peek().type not in ("}", "EOF"):
                expr = self.parse_expression()
            return ReturnStmt(expr)
        if tok.type == "FUNC":
            return self.parse_func_decl()
        if tok.type == "OP" and tok.value == "{":
            return self.parse_block()
        if tok.type == "ID" and len(self.tokens) > self.pos + 1:
            next_tok = self.tokens[self.pos + 1] 
            if next_tok.type == "OP" and next_tok.value == ":":
                decl = self.parse_var_decl_content()
                return VarDeclStmt(decl)
        expr = self.parse_expression()
        if self.peek().type == "OP" and self.peek().value == "=":
            self.next()
            val = self.parse_expression()
            return VarAssign(expr, val)
        else:
            return ExprStmt(expr)
        
    def parse_var_decl_content(self) -> VarDecl:
        name = self.expect("ID").value  
        colon_tok = self.expect("OP")
        if colon_tok.value != ":":
            raise ParserError(f"Expected ':' but got '{colon_tok.value}' at {colon_tok.line}:{colon_tok.col}")
        type_tok = self.next()
        valid_types = ("ID", "NUMBER", "INT", "BOOL", "STRING", "C_CHANNEL")
        if type_tok.type not in valid_types:
             raise ParserError(f"Expected a type identifier but got {type_tok.type} ('{type_tok.value}') at {type_tok.line}:{type_tok.col}")
        type_name = type_tok.value
        init = None
        if self.peek().type == "OP" and self.peek().value == "=":
            self.next()
            init = self.parse_expression()
        return VarDecl(name, type_name, init)

    def parse_send(self) -> SendStmt:
        self.expect("SEND"); self.expect("(")
        ch = self.parse_expression()
        self.expect(",")
        data = self.parse_expression()
        self.expect(")");
        return SendStmt(ch, data)

    def parse_receive(self) -> ReceiveStmt:
        self.expect("RECEIVE"); self.expect("(")
        ch = self.parse_expression()
        self.expect(")")
        return ReceiveStmt(ch, None)
    
    def parse_while(self) -> WhileStmt:
        self.expect("WHILE")
        self.expect_symbol("(", "Esperado '(' para iniciar a condição do while")
        cond = self.parse_expression()
        self.expect_symbol(")", "Esperado ')' para fechar a condição do while")
        body = self.parse_stmt()
        return WhileStmt(cond, body)