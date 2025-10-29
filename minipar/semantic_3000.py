from typing import List, Optional, Dict, Any
from ast_251018_215806 import AST, Program, Block, VarRef, BinaryOp, IfStmt, WhileStmt, FuncDecl, VarDecl, Literal, VarAssign, VarDeclStmt, Call, ReturnStmt, DictLiteral, ListLiteral, IndexAccess
from symbol_3000 import SymbolEntry, SymbolTable, SemanticError

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
        ('bool', '&&', 'bool'): 'bool'}
    
    def __init__(self):
        super().__init__()
        self.current_scope: SymbolTable = SymbolTable()
        self.current_return_type: Optional[str] = None
        self.errors: List[str] = []

    def report_error(self, msg: str): 
        self.errors.append(msg)

    def analyze(self, program: Program) -> Program:
        self.visit(program)
        if self.errors: 
            raise SemanticError(f"Análise semântica falhou com {len(self.errors)} erros:\n" + "\n".join(self.errors))
        return program

    def visit_Program(self, node: Program): self.generic_visit(node)
    
    def visit_Block(self, node: Block):
        self.current_scope = self.current_scope.enter_scope()
        self.generic_visit(node)
        self.current_scope = self.current_scope.exit_scope()
    
    def visit_FuncDecl(self, node: FuncDecl):
        self.current_scope.define(SymbolEntry(node.name, node.ret_type, 'FUNC'))
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
        setattr(node, 'ast_type', 'dict')
        for key, value in node.pairs:
            self.visit(key)
            self.visit(value)

    def visit_ListLiteral(self, node: ListLiteral):
        setattr(node, 'ast_type', 'list')
        if node.elements:
            first_type = self.visit(node.elements[0])
            for element in node.elements:
                self.visit(element)
                element_type = getattr(element, 'ast_type', 'error')
                if element_type != first_type: self.report_error("Lista deve ser homogênea...")

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
        for arg in node.args: self.visit(arg)
        setattr(node, 'ast_type', 'number')
