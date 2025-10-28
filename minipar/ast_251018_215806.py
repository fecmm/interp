from dataclasses import dataclass
from typing import List, Optional

class AST: pass

@dataclass
class Program(AST):
    classes: List['ClassDecl']
    stmts: List['Stmt']

@dataclass
class ClassDecl(AST):
    name: str
    base: Optional[str]
    fields: List['VarDecl']
    methods: List['FuncDecl']

@dataclass
class VarDecl(AST):
    name: str
    type_name: str
    init: Optional['Expr']

@dataclass
class FuncDecl(AST):
    name: str
    params: List[VarDecl]
    ret_type: str
    body: 'Block'

# Statements
class Stmt(AST): pass

@dataclass
class Block(Stmt):
    stmts: List[Stmt]

@dataclass
class IfStmt(Stmt):
    cond: 'Expr'
    then_branch: Stmt
    else_branch: Optional[Stmt]

@dataclass
class WhileStmt(Stmt):
    cond: 'Expr'
    body: Stmt

@dataclass
class ExprStmt(Stmt):
    expr: 'Expr'

@dataclass
class VarAssign(Stmt):
    target: 'Expr' 
    value: 'Expr'

@dataclass
class VarDeclStmt(Stmt):
    decl: VarDecl

@dataclass
class SeqBlock(Stmt):
    block: Block

@dataclass
class ParBlock(Stmt):
    block: Block

@dataclass
class SendStmt(Stmt):
    channel_expr: 'Expr'
    data_expr: 'Expr'

@dataclass
class ReceiveStmt(Stmt):
    channel_expr: 'Expr'
    target: Optional[str] 

@dataclass
class PrintStmt(Stmt):
    expr: 'Expr'

@dataclass
class ReturnStmt(Stmt): 
    expr: Optional['Expr']

@dataclass
class BreakStmt(Stmt): 
    pass

# Expressoes
class Expr(AST): pass

@dataclass
class Literal (Expr):
    value: object

@dataclass
class VarRef(Expr):
    name: str

@dataclass
class BinaryOp(Expr):
    left: Expr
    op: str
    right: Expr

@dataclass
class UnaryOp(Expr):
    op: str
    expr: Expr

@dataclass
class Call(Expr):
    callee: Expr
    args: List[Expr]

@dataclass
class NewObj(Expr):
    class_name: str

@dataclass
class AttrAccess(Expr):
    obj: Expr
    attr: str