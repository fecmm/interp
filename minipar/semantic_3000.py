from typing import List, Optional, Dict, Any
from ast_251018_215806 import AST, Program, Block, VarRef, BinaryOp, IfStmt, WhileStmt, FuncDecl, VarDecl, Literal, VarAssign, VarDeclStmt, Call, ReturnStmt, DictLiteral, ListLiteral, IndexAccess, NewExpr, ParStmt, SendStmt, SeqStmt, ReceiveExpr, MethodCall
from symbol_3000 import SymbolEntry, SymbolTable, SemanticError, FunctionSymbolEntry

class ASTVisitor:
    def visit(self, node: AST, *args, **kwargs):
        method_name = f'visit_{node.__class__.__name__}'
        visitor_method = getattr(self, method_name, self.generic_visit)
        return visitor_method(node, *args, **kwargs)

    def generic_visit(self, node: AST, *args, **kwargs):
        if not hasattr(node, '__dataclass_fields__'):
             return 
        for field in node.__dataclass_fields__:
            value = getattr(node, field)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        self.visit(item, *args, **kwargs)
            elif isinstance(value, AST):
                self.visit(value, *args, **kwargs)

class SemanticAnalyzer(ASTVisitor):
    COMPATIBLE_TYPES = {
        ('number', '+', 'number'): 'number', 
        ('number', '-', 'number'): 'number',
        ('number', '*', 'number'): 'number', 
        ('number', '/', 'number'): 'number',
        ('number', '==', 'number'): 'bool', 
        ('number', '<', 'number'): 'bool',

        ('number', '>=', 'number'): 'bool', 
        ('number', '>', 'number'): 'bool',
        ('number', '<=', 'number'): 'bool',
        ('number', '!=', 'number'): 'bool',

        ('bool', '==', 'bool'): 'bool',
        ('bool', '||', 'bool'): 'bool',
        ('bool', '&&', 'bool'): 'bool',
        ('string', '==', 'string'): 'bool',
        ('string', '!=', 'string'): 'bool',
        ('number', '==', 'number'): 'bool'}
    
    BUILTIN_FUNCTIONS = {
        "print": (['any'], 'void'), 
        "len": (['list'], 'number'), 
        "sum": (['list'], 'number'),
        "exp": (['number'], 'number'),
        "pow": (['number', 'number'], 'number'),
        "random": ([], 'number'),
        "range": (['number'], 'list'),
        "sleep": (['number'], 'void'),
        "input": (['string'], 'string'),
        "close": ([], 'void')
    }
    
    def __init__(self):
        super().__init__()
        self.global_scope = SymbolTable()
        self.current_scope: SymbolTable = SymbolTable()
        self.current_return_type: Optional[str] = None
        self.errors: List[str] = []
        self._initialize_builtins()

    def _initialize_builtins(self):
        for name, (param_types, return_type) in self.BUILTIN_FUNCTIONS.items():
            entry = FunctionSymbolEntry(name, param_types, return_type, kind="builtin_func")
            self.current_scope.define(entry)

    def report_error(self, msg: str): 
        self.errors.append(msg)

    def analyze(self, program: Program) -> Program:
        self.visit(program)
        if self.errors: 
            raise SemanticError(f"Análise semântica falhou com {len(self.errors)} erros:\n" + "\n".join(self.errors))
        return program

    def visit_Program(self, node: Program): 
        self.generic_visit(node)
    
    def visit_Block(self, node: Block):
        self.current_scope = self.current_scope.enter_scope()
        self.generic_visit(node)
        self.current_scope = self.current_scope.exit_scope()
    
    def visit_FuncDecl(self, node: FuncDecl):
        func_entry = FunctionSymbolEntry(name=node.name, param_types=[p.type_name for p in node.params], return_type=node.ret_type, kind='function')
        self.current_scope.define(func_entry) 
        self.current_scope = self.current_scope.enter_scope()
        self.current_return_type = node.ret_type
        for param in node.params:
            self.current_scope.define(SymbolEntry(param.name, param.type_name, 'VAR'))
        self.visit(node.body)
        self.current_scope = self.current_scope.exit_scope()
        self.current_return_type = None

    def visit_VarDeclStmt(self, node: VarDeclStmt):
        self.current_scope.define(SymbolEntry(node.decl.name, node.decl.type_name, 'VAR'))
        if node.decl.init:
            self.visit(node.decl.init)
            init_type = getattr(node.decl.init, 'ast_type', 'error')
            if init_type != node.decl.type_name: 
                self.report_error(f"Incompatibilidade na declaração de '{node.decl.name}': esperado {node.decl.type_name}, recebido {init_type}.")

    def visit_VarRef(self, node: VarRef):
        entry = self.current_scope.resolve(node.name)
        if not entry:
            self.report_error(f"Variável '{node.name}' não declarada.")
            setattr(node, 'ast_type', 'error')
        else:
            setattr(node, 'ast_type', entry.type_name) 

    def visit_BinaryOp(self, node: BinaryOp):
        self.visit(node.left)
        self.visit(node.right)
        left_type = getattr(node.left, 'ast_type', 'error')
        right_type = getattr(node.right, 'ast_type', 'error')
        op = node.op
        key = (left_type, op, right_type)
        if key in self.COMPATIBLE_TYPES:
            setattr(node, 'ast_type', self.COMPATIBLE_TYPES[key])
        else:
            self.report_error(f"Incompatibilidade de tipos na operação '{op}': {left_type} {op} {right_type}.")
            setattr(node, 'ast_type', 'error')

    def visit_VarAssign(self, node: VarAssign):
        self.visit(node.target); self.visit(node.value)
        target_type = getattr(node.target, 'ast_type', 'error')
        value_type = getattr(node.value, 'ast_type', 'error')
        if target_type != value_type: 
            self.report_error(f"Incompatibilidade de tipos na atribuição: esperado {target_type}, recebido {value_type}.")

    def visit_IfStmt(self, node: IfStmt):
        self.visit(node.cond)
        cond_type = getattr(node.cond, 'ast_type', 'error')
        if cond_type != 'bool': 
            self.report_error(f"Condição 'if' deve ser 'bool', recebido '{cond_type}'.")
        self.visit(node.then_branch); 
        if node.else_branch: 
            self.visit(node.else_branch)

    def visit_WhileStmt(self, node: WhileStmt):
        self.visit(node.cond)
        cond_type = getattr(node.cond, 'ast_type', 'error')
        if cond_type != 'bool': 
            self.report_error(f"Condição 'while' deve ser 'bool', recebido '{cond_type}'.")
        self.visit(node.body)

    def visit_ReturnStmt(self, node: ReturnStmt):
        if node.expr:
            self.visit(node.expr)
            return_expr_type = getattr(node.expr, 'ast_type', 'error')
            if return_expr_type != self.current_return_type: 
                self.report_error(f"Retorno inválido: esperado {self.current_return_type}, recebido {return_expr_type}.")
    
    def visit_Literal(self, node: Literal):
        if isinstance(node.value, bool): 
            setattr(node, 'ast_type', 'bool')
        elif isinstance(node.value, int): 
            setattr(node, 'ast_type', 'number')
        elif isinstance(node.value, float): 
            setattr(node, 'ast_type', 'number')
        elif isinstance(node.value, str): 
            setattr(node, 'ast_type', 'string')
        else: 
            setattr(node, 'ast_type', 'unknown')

    def visit_DictLiteral(self, node: DictLiteral):
        key_types_seen = set()
        value_types_seen = set()
        for key_node, value_node in node.pairs:
            self.visit(key_node)
            key_type = getattr(key_node, 'ast_type', 'error')
            self.visit(value_node)
            value_type = getattr(value_node, 'ast_type', 'error')
            if key_type not in ('string', 'number', 'bool'):
                self.report_error(f"Erro Semântico: Tipo de chave '{key_type}' não permitido para dicionários (deve ser string, number ou bool).")
            if key_type != 'error':
                key_types_seen.add(key_type)
            if value_type != 'error':
                value_types_seen.add(value_type)
        if len(key_types_seen) > 1:
            self.report_error("Erro Semântico: Todas as chaves do dicionário devem ser do mesmo tipo.")
        if len(value_types_seen) > 1:
            self.report_error("Erro Semântico: Todos os valores do dicionário devem ser do mesmo tipo.")
        setattr(node, 'ast_type', 'dict')

    def visit_ListLiteral(self, node: ListLiteral):
        setattr(node, 'ast_type', 'list')
        if node.elements:
            first_type = self.visit(node.elements[0])
            for element in node.elements:
                self.visit(element)
                element_type = getattr(element, 'ast_type', 'error')
                if element_type != first_type: 
                    self.report_error("Lista deve ser homogênea...")

    def visit_IndexAccess(self, node: IndexAccess):
        self.visit(node.target)
        target_type = getattr(node.target, 'ast_type', 'error')
        self.visit(node.index)
        index_type = getattr(node.index, 'ast_type', 'error')
        if target_type == 'list':
            if index_type != 'number':
                self.report_error(f"Índice de lista deve ser 'number', recebido '{index_type}'.")
            setattr(node, 'ast_type', 'unknown')
        elif target_type == 'dict':
            if index_type not in ('string', 'number'):
                self.report_error(f"Chave de dicionário inválida: esperado 'string' ou 'number', recebido '{index_type}'.")
            setattr(node, 'ast_type', 'unknown') 
        else:
            self.report_error(f"Acesso por índice/chave ('[]') não é suportado para o tipo '{target_type}'.")

    def visit_Call(self, node: Call):
        self.visit(node.callee) 
        if isinstance(node.callee, VarRef):
            func_name = node.callee.name
        elif hasattr(node.callee, 'name'):
            func_name = node.callee.name
        else:
            self.report_error(f"O alvo da chamada (callee) '{node.callee}' é inválido.")
            setattr(node, 'ast_type', 'error')
            return 'error'
        func_entry = self.current_scope.resolve(func_name)
        if not func_entry or func_entry.kind not in ("function", "builtin_func"):
            self.report_error(f"Função '{func_name}' não declarada ou não é uma função.")
            setattr(node, 'ast_type', 'error')
            return 'error'
        expected_types = func_entry.param_types
        actual_types = []
        for arg in node.args:
            self.visit(arg)
            actual_types.append(getattr(arg, 'ast_type', 'error'))
        if len(expected_types) != len(actual_types):
            self.report_error(f"Chamada para '{func_name}' tem {len(actual_types)} argumentos, mas esperava {len(expected_types)}.")
        else:
            for exp_t, act_t in zip(expected_types, actual_types):
                if exp_t != 'any' and exp_t != act_t:
                    self.report_error(f"Incompatibilidade no argumento da chamada para '{func_name}': esperado {exp_t}, recebido {act_t}.")
        return_type = func_entry.return_type
        setattr(node, 'ast_type', return_type)
        return return_type

    def visit_NewExpr(self, node: NewExpr):
        if node.target_type == 'c_channel':
            setattr(node, 'ast_type', 'c_channel')
        else:
            self.report_error(f"Criação 'new' de tipo '{node.target_type}' não suportada ou desconhecida.")
            setattr(node, 'ast_type', 'error')
            
    def visit_ParStmt(self, node: ParStmt):
        self.generic_visit(node)

    def visit_SeqStmt(self, node: SeqStmt):
        self.generic_visit(node) 

    def visit_SendStmt(self, node: SendStmt):
        self.visit(node.channel)
        self.visit(node.data)
        ch_type = getattr(node.channel, 'ast_type', 'error')
        data_type = getattr(node.data, 'ast_type', 'error') 
        if ch_type != 'c_channel':
            self.report_error(f"O alvo do SEND deve ser do tipo 'c_channel', mas recebeu '{ch_type}'.")
            setattr(node, 'ast_type', 'error')
            return 
        if data_type != 'string':
            self.report_error(f"O tipo de dado enviado ({data_type}) não é o tipo esperado 'string'.")
        setattr(node, 'ast_type', 'string')
            
    def visit_ReceiveExpr(self, node: ReceiveExpr):
        self.visit(node.channel)
        ch_type = getattr(node.channel, 'ast_type', 'error')
        if ch_type != 'c_channel':
            self.report_error(f"O alvo do RECEIVE deve ser do tipo 'c_channel', mas recebeu '{ch_type}'.")
            setattr(node, 'ast_type', 'error')
        else:
            setattr(node, 'ast_type', 'number')
    
    def visit_CChannelClientStmt(self, node):
        self.current_scope.define(SymbolEntry(node.name, 'c_channel', 'VAR'))
        self.visit(node.address)
        self.visit(node.port)
        setattr(node, 'ast_type', 'c_channel')

    def visit_SChannelServerStmt(self, node):
        self.current_scope.define(SymbolEntry(node.name, 's_channel', 'VAR'))
        self.visit(node.init) 
        setattr(node, 'ast_type', 's_channel')

    def visit_MethodCall(self, node: MethodCall):
        self.visit(node.target)
        target_type = getattr(node.target, 'ast_type', 'error')
        if target_type == 'c_channel':
            if node.method_name == 'send':
                if len(node.args) != 1:
                    self.report_error(f"O método 'send' em c_channel esperava 1 argumento, mas recebeu {len(node.args)}.")
                self.visit(node.args[0])
                data_type = getattr(node.args[0], 'ast_type', 'error')
                if data_type != 'string':
                    self.report_error(f"Argumento do 'send' em c_channel deve ser 'string', mas recebeu '{data_type}'.")
                setattr(node, 'ast_type', 'string')
                return 'string'
            elif node.method_name == 'close':
                if len(node.args) != 0:
                     self.report_error(f"O método 'close' em c_channel não esperava argumentos, mas recebeu {len(node.args)}.")
                setattr(node, 'ast_type', 'void')
                return 'void'
            else:
                self.report_error(f"Método '{node.method_name}' não suportado pelo tipo '{target_type}'.")
                setattr(node, 'ast_type', 'error')
                return 'error'
        else:
            self.report_error(f"Chamada de método em alvo de tipo não suportado: '{target_type}'.")
            setattr(node, 'ast_type', 'error')
            return 'error'
