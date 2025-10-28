# interpreter.py

from typing import List, Optional, Dict, Any
from ast_251018_215806 import Program, Block, VarRef, BinaryOp, IfStmt, WhileStmt, FuncDecl, Literal, VarAssign, VarDeclStmt, Call, ReturnStmt, PrintStmt, AST

class RuntimeError(Exception): pass

class ReturnException(Exception): 
    def __init__(self, value):
        self.value = value

class BreakException(Exception): pass 

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

class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.values: Dict[str, Any] = {}
        self.parent = parent

    def enter_scope(self) -> 'Environment':
        return Environment(parent=self)
    
    def exit_scope(self) -> Optional['Environment']:
        return self.parent
    
    def define(self, name: str, value: Any):
        self.values[name] = value

    def assign(self, name: str, value: Any):
        env = self.resolve(name)
        if env:
            env.values[name] = value
        else:
            raise RuntimeError(f"Variável não definida: {name}")
        
    def lookup(self, name: str) -> Any:
        env = self.resolve(name)
        if env:
            return env.values[name]
        raise RuntimeError(f"Variável não definida: {name}")
    
    def resolve(self, name: str) -> Optional['Environment']:
        current = self
        while current:
            if name in current.values:
                return current
            current = current.parent
        return None

class Interpreter(ASTVisitor): 
    def __init__(self):
        super().__init__()
        self.global_env = Environment()
        self.env: Environment = self.global_env
        self.functions: Dict[str, FuncDecl] = {} 

    def interpret(self, ast: Program):
        for stmt in ast.stmts:
            if isinstance(stmt, FuncDecl):
                self.visit(stmt)
        for stmt in ast.stmts:
             if not isinstance(stmt, FuncDecl):
                self.visit(stmt)

    def visit_Block(self, node: Block):
        self.env = self.env.enter_scope()
        try:
            for stmt in node.stmts: 
                self.visit(stmt)
        finally:
            self.env = self.env.exit_scope()

    def visit_VarDeclStmt(self, node: VarDeclStmt):
        init_val = None
        if node.decl.init: 
            init_val = self.visit(node.decl.init)
        if init_val is None:
            if node.decl.type_name == 'number':
                init_val = 0
            elif node.decl.type_name == 'bool':
                init_val = False
        self.env.define(node.decl.name, init_val)

    def visit_VarAssign(self, node: VarAssign):
        name = node.target.name 
        value = self.visit(node.value)
        self.env.assign(name, value) 

    def visit_PrintStmt(self, node: PrintStmt):
        value = self.visit(node.expr)
        print(f"{value}")

    def visit_FuncDecl(self, node: FuncDecl):
        self.functions[node.name] = node
        self.env.define(node.name, node) 

    def visit_ReturnStmt(self, node: ReturnStmt):
        if node.expr:
            value = self.visit(node.expr)
        else:
            value = None
        raise ReturnException(value) 

    def visit_IfStmt(self, node: IfStmt):
        if self.visit(node.cond): 
            self.visit(node.then_branch)
        elif node.else_branch: 
            self.visit(node.else_branch)

    def visit_WhileStmt(self, node: WhileStmt):
        while self.visit(node.cond):
            try:
                self.visit(node.body)
            except BreakException:
                break 
            except ReturnException as e:
                raise e 
    
    def visit_BreakStmt(self, node):
        raise BreakException()

    def visit_Literal(self, node: Literal):
        return node.value

    def visit_VarRef(self, node: VarRef):
        return self.env.lookup(node.name)

    def visit_BinaryOp(self, node: BinaryOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op
        if op == '+': 
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            if isinstance(left, int):
                return left // right #divisao inteiro
            else:
                left / right #divisao float
        if op == '==':
            return left == right
        if op == '<':
            return left < right
        if op == '>':
            return left > right
        if op == '&&':
            return left and right
        if op == '||':
            return left or right
        raise RuntimeError(f"Operador '{op}' não suportado.")

    def visit_Call(self, node: Call):
        func_name = node.callee.name 
        func_decl = self.functions.get(func_name)
        if not func_decl:
            raise RuntimeError(f"Função '{func_name}' não definida.")
        evaluated_args = [self.visit(arg) for arg in node.args]
        self.env = self.env.enter_scope()
        for param, arg_val in zip(func_decl.params, evaluated_args):
            self.env.define(param.name, arg_val)
        result = None
        try:
            self.visit(func_decl.body)
        except ReturnException as e:
            result = e.value
        finally:
            self.env = self.env.exit_scope()
        return result