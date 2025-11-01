from dataclasses import dataclass
from typing import List, Tuple, Optional, Any

class AST: 
    pass

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

@dataclass
class FieldAccess(AST):
    target: AST
    member_name: str

@dataclass
class MethodCall(AST):
    target: AST 
    method_name: str
    args: List[AST]

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
class ForStmt(Stmt):
    decl: VarDecl 
    iterable: Any  
    body: Any

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
    expressions: List['Expr']

@dataclass
class ReturnStmt(Stmt): 
    expr: Optional['Expr']

@dataclass
class BreakStmt(Stmt): 
    pass

@dataclass
class ParStmt(Stmt):
    stmts: List[Any]

@dataclass
class SeqStmt(Stmt):
    stmts: List[Any]

@dataclass
class SendStmt(Stmt):
    channel: Any
    data: Any

@dataclass
class CChannelClientStmt(Stmt): 
    name: str
    address: AST 
    port: AST

# Expressoes
class Expr(AST): pass

@dataclass
class Literal (Expr):
    value: object

@dataclass
class DictLiteral(Expr):
    pairs: List[Tuple['Expr', 'Expr']] 

@dataclass
class ListLiteral(Expr):
    elements: List['Expr']
    
@dataclass
class IndexAccess(Expr):
    target: 'Expr'   
    index: 'Expr' 

@dataclass
class PropertyAccess(Expr):
    target: Any          
    property_name: str   

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

@dataclass
class ReceiveExpr(Expr):
    channel: Any

@dataclass
class NewExpr(Expr):
    target_type: str
    args: List[Any]
