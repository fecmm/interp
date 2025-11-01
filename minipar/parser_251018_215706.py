from typing import List
from minipar.lexer_251018_215612 import Token, Lexer
from minipar.ast_251018_215806 import *

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
        self.expect_symbol("{", "Esperado '{' para iniciar a classe")
        fields = []
        methods = []
        while self.peek().type != "OP" or self.peek().value != "}":
            if self.peek().type == "VAR": 
                fields.append(self.parse_var_decl())
            elif self.peek().type == "FUNC": 
                methods.append(self.parse_func_decl())
            else:
                raise ParserError(f"Unexpected token in class body: {self.peek().type} ('{self.peek().value}')")
        self.expect_symbol("}", "Esperado '}' para fechar a classe")
        return ClassDecl(name, base, fields, methods)

    def parse_var_decl(self) -> VarDecl:
        if self.peek().type == "VAR":
            self.expect("VAR")
        name = self.expect("ID").value
        self.expect_symbol(":", "Esperado ':' para tipo")
        type_tok = self.next()
        if type_tok.type not in ("ID", "NUMBER", "INT", "BOOL", "STRING", "C_CHANNEL"):
             raise ParserError(f"Expected type identifier but got {type_tok.type}")
        type_name = type_tok.value
        init = None
        if self.peek().type == "OP" and self.peek().value == "=":
            self.next()
            init = self.parse_expression()
        return VarDecl(name, type_name, init)

    def expect_symbol(self, expected_value: str, error_message: str = ""):
            tok = self.expect("OP")
            if tok.value != expected_value:
                msg = error_message if error_message else f"Expected '{expected_value}' but got '{tok.value}'"
                raise ParserError(f"{msg} at {tok.line}:{tok.col}")
            return tok

    def _consume_terminator(self):
        if self.peek().type == "OP" and self.peek().value == ";":
            self.next()
        elif self.peek().type == "OP" and self.peek().value == "}":
            pass
        elif self.peek().type == "EOF":
            pass
        elif self.peek().type in ("VAR", "FUNC", "IF", "WHILE", "PRINT", "BREAK", "RETURN", "SEND", "RECEIVE"):
            pass
        elif self.peek().type == "ID":
            pass 
        else:
            raise ParserError(f"Esperado ';' após instrução, '}}' ou fim de arquivo, mas encontrado '{self.peek().value}' na linha {self.peek().line}:{self.peek().col}.")

    def parse_func_decl(self) -> FuncDecl:
        self.expect("FUNC") 
        name = self.expect("ID").value
        self.expect_symbol("(", "Erro na abertura de parâmetros")
        valid_types = ("ID", "NUMBER", "INT", "BOOL", "STRING", "C_CHANNEL") 
        params = []
        if self.peek().type == "OP" and self.peek().value == ")":
            self.next() 
        else:
            while True:
                p_name = self.expect("ID").value
                self.expect_symbol(":", "Erro no separador de tipo do parâmetro")
                p_type_tok = self.next()
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
            if '.' in tok.value:
                return Literal(float(tok.value))
            else:
                return Literal(int(tok.value))
        if tok.type == "OP" and tok.value == "{":
            pairs = []
            if not (self.peek().type == "OP" and self.peek().value == "}"):
                while True:
                    key = self.parse_expression() 
                    self.expect_symbol(":", error_message="Esperado ':' em literal de dicionário")
                    value = self.parse_expression() 
                    pairs.append((key, value))
                    if self.peek().type == "OP" and self.peek().value == ",":
                        self.next() 
                        if self.peek().type == "OP" and self.peek().value == "}":
                            break 
                        continue
                    elif self.peek().type == "OP" and self.peek().value == "}":
                        break
                    else:
                        raise ParserError(f"Token inesperado '{self.peek().value}' em literal de dicionário. Esperado ',' ou '}}'.")
            self.expect_symbol("}", error_message="Esperado '}' para fechar literal de dicionário")
            return DictLiteral(pairs=pairs)
        if tok.type == "OP" and tok.value == "[":
            elements = []
            if not (self.peek().type == "OP" and self.peek().value == "]"):
                while True:
                    element = self.parse_expression()
                    elements.append(element)
                    if self.peek().type == "OP" and self.peek().value == ",":
                        self.next()
                        if self.peek().type == "OP" and self.peek().value == "]":
                            break 
                        continue
                    elif self.peek().type == "OP" and self.peek().value == "]":
                        break
                    else:
                        raise ParserError(f"Token inesperado '{self.peek().value}' em literal de lista. Esperado ',' ou ']'.")
            self.expect_symbol("]", error_message="Esperado ']' para fechar literal de lista")
            return ListLiteral(elements=elements)
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
        if tok.type == "RECEIVE":
            return self.parse_receive_expr()
        if tok.type == "NEW":
            return self.parse_new()
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
            if v in ("["):
                return 85
            if v == ".":
                return 90
        if tok.type == "(":
            return 80
        return 0

    def led(self, tok: Token, left):
        if tok.type == "OP":
            op = tok.value
            if op in ("+", "-", "*", "/", "==", "!=", "<", ">", "<=", ">=", "&&", "||"):
                right = self.parse_expression(self.lbp(tok))
                return BinaryOp(left, op, right)
            if op == "[":
                index_expr = self.parse_expression() 
                self.expect_symbol("]", error_message="Esperado ']' para fechar o acesso ao índice")
                return IndexAccess(target=left, index=index_expr)
            if op == ".":
                member_tok = self.expect("ID")
                member_name = member_tok.value
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
                    self.expect_symbol(")", "Esperado ')' para fechar argumentos da chamada de método")
                    return MethodCall(left, member_name, args)
                else:
                    return FieldAccess(left, member_name)
        if tok.type == "(":
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
        if tok.type == "IF": 
            return self.parse_if() 
        if tok.type == "WHILE": 
            return self.parse_while()
        if tok.type == "FUNC":
            return self.parse_func_decl()
        if tok.type == "OP" and tok.value == "{":
            return self.parse_block()
        elif tok.type == "C_CHANNEL": 
            return self.parse_c_channel_client_stmt()
        if tok.type == "PAR":
            return self.parse_par()
        if tok.type == "SEQ":
            return self.parse_seq()
        stmt: Stmt = None
        if tok.type == "VAR":
            self.expect("VAR")
            stmt = VarDeclStmt(self.parse_var_decl_content()) 
        elif tok.type == "ID":
            if len(self.tokens) > self.pos + 1 and self.tokens[self.pos + 1].value == ":":
                name = self.next().value
                self.expect_symbol(":", "Esperado ':' após nome de variável para declaração")
                type_tok = self.next()
                valid_types = ("ID", "NUMBER", "INT", "BOOL", "STRING", "C_CHANNEL")
                if type_tok.type not in valid_types:
                    raise ParserError(f"Esperado um identificador de tipo, mas encontrado {type_tok.type} ('{type_tok.value}') em {type_tok.line}:{type_tok.col}")
                type_name = type_tok.value
                init = None
                if self.peek().type == "OP" and self.peek().value == "=":
                    self.next()
                    init = self.parse_expression()
                stmt = VarDeclStmt(VarDecl(name, type_name, init))
            else:
                expr = self.parse_expression()
                
                if self.peek().type == "OP" and self.peek().value == "=":
                    self.next()
                    val = self.parse_expression()
                    stmt = VarAssign(expr, val)
                else:
                    stmt = ExprStmt(expr)
        elif tok.type == "SEND": 
            stmt = self.parse_send_stmt()
        elif tok.type == "PRINT": 
            stmt = self.parse_print_stmt() 
        elif tok.type == "BREAK": 
            self.next()
            stmt = BreakStmt()
        elif tok.type == "RETURN": 
            self.next()
            expr = None
            if self.peek().type != "OP" or self.peek().value not in ("}", ";"):
                expr = self.parse_expression()
            stmt = ReturnStmt(expr)
        else:
            raise ParserError(f"Instrução inesperada: '{tok.value}' na linha {tok.line}:{tok.col}")
        return stmt
        
    def parse_var_decl_content(self) -> VarDecl:
        name = self.expect("ID").value  
        colon_tok = self.expect_symbol(":", "Esperado ':' para tipo")
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
    
    def parse_while(self) -> WhileStmt:
        self.expect("WHILE")
        self.expect_symbol("(", "Esperado '(' para iniciar a condição do while")
        cond = self.parse_expression()
        self.expect_symbol(")", "Esperado ')' para fechar a condição do while")
        body = self.parse_stmt()
        return WhileStmt(cond, body)
    
    def parse_block_stmts(self) -> List[Any]:
        self.expect_symbol("{", "Esperado '{' para iniciar bloco de instruções")
        stmts = []
        while self.peek().type != "OP" or self.peek().value != "}":
            if self.peek().type == "EOF":
                raise ParserError("Esperado '}' mas atingiu o fim do arquivo.")
            stmts.append(self.parse_stmt())
        self.expect_symbol("}", "Esperado '}' para fechar bloco de instruções")
        return stmts

    def parse_par(self) -> ParStmt:
        self.expect("PAR")
        stmts = self.parse_block_stmts()
        return ParStmt(stmts)

    def parse_seq(self) -> SeqStmt:
        self.expect("SEQ")
        stmts = self.parse_block_stmts()
        return SeqStmt(stmts)

    def parse_new(self) -> NewExpr:
        type_tok = self.expect("C_CHANNEL")
        self.expect_symbol("(", "Esperado '(' após construtor 'new'")
        args = [] 
        self.expect_symbol(")", "Esperado ')' após construtor 'new'")
        return NewExpr(target_type=type_tok.value, args=args)
        
    def parse_receive_expr(self) -> ReceiveExpr:
        tok = self.expect("ID")
        if tok.value != "receive":
             raise ParserError(f"Esperado 'receive' mas encontrado '{tok.value}'")
        self.expect_symbol("(", "Esperado '(' em RECEIVE")
        ch = self.parse_expression()
        self.expect_symbol(")", "Esperado ')' em RECEIVE")
        return ReceiveExpr(channel=ch)

    def parse_send_stmt(self) -> SendStmt:
        tok = self.expect("ID")
        if tok.value != "send":
            raise ParserError(f"Esperado 'send' mas encontrado '{tok.value}'")
        self.expect_symbol("(", "Esperado '(' em SEND")
        ch = self.parse_expression()
        self.expect_symbol(",", "Esperado ',' para separar canal e dado em SEND")
        data = self.parse_expression()
        self.expect_symbol(")", "Esperado ')' em SEND")
        return SendStmt(channel=ch, data=data)
    
    def parse_print_stmt(self) -> PrintStmt:
        self.expect("PRINT")
        self.expect_symbol("(", "Esperado '(' para iniciar a lista de argumentos do print")
        expressions = []
        if not (self.peek().type == "OP" and self.peek().value == ")"):
            while True:
                expr = self.parse_expression()
                expressions.append(expr)
                if self.peek().type == "OP" and self.peek().value == ",":
                    self.next()
                elif self.peek().type == "OP" and self.peek().value == ")":
                    break
                else:
                    raise ParserError(f"Token inesperado '{self.peek().value}' após argumento em print. Esperado ',' ou ')'.")
        self.expect_symbol(")", "Esperado ')' para fechar argumentos do print")
        return PrintStmt(expressions=expressions)
    
    def parse_c_channel_client_stmt(self) -> CChannelClientStmt:
        self.expect("C_CHANNEL")
        name = self.expect("ID").value
        self.expect_symbol("{", "Esperado '{' para iniciar a definição do canal cliente")
        address_expr = self.parse_expression()
        self.expect_symbol(",", "Esperado ',' para separar endereço e porta")
        port_expr = self.parse_expression()
        self.expect_symbol("}", "Esperado '}' para fechar a definição do canal cliente")
        return CChannelClientStmt(name=name, address=address_expr, port=port_expr)
