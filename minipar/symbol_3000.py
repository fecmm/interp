from typing import Optional, Dict, List

class SemanticError(Exception): 
    pass

class SymbolEntry:
    def __init__(self, name: str, type_name: str, kind: str):
        self.name = name
        self.type_name = type_name
        self.kind = kind

class FunctionSymbolEntry(SymbolEntry):
    def __init__(self, name: str, param_types: List[str], return_type: str, kind: str = "function"):
        super().__init__(name, return_type, kind) 
        self.param_types = param_types
        self.return_type = return_type

class SymbolTable:
    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.symbols: Dict[str, SymbolEntry] = {} 
        self.parent = parent
        
    def enter_scope(self) -> 'SymbolTable':
        return SymbolTable(parent=self)
    
    def exit_scope(self) -> Optional['SymbolTable']:
        return self.parent
    
    def define(self, entry: SymbolEntry):
        if entry.name in self.symbols:
            raise SemanticError(f"Erro semântico: Símbolo '{entry.name}' já definido neste escopo.")
        self.symbols[entry.name] = entry
        
    def resolve(self, name: str) -> Optional[SymbolEntry]:
        current_scope = self
        while current_scope:
            if name in current_scope.symbols:
                return current_scope.symbols[name]
            current_scope = current_scope.parent
        return None
