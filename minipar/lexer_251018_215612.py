import re
from dataclasses import dataclass
from typing import List

@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int

class LexerError(Exception): pass

class Lexer:
    TOKEN_SPEC = [
        ("NUMBER", r"\d+(\.\d+)?"), #modificação aqui 
        ("STRING", r"\"(\\.|[^\"])*\""),
        ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
        ("MULTICOMMENT", r"/\*[\s\S]*?\*/"), #multicomentarios
        ("NEWLINE", r"\n"),
        ("SKIP", r"[ \t\r]+"), #espaço como caractere a se ignorar
        ("COMMENT", r"#.*"),
        ("OP",
         r"==|!=|<=|>=|->|&&|\|\||[+\-*/<>=!,.;:(){}\[\].]"),
    ]
    
    KEYWORDS = {
        "class","extends","new","if","else","while","for","func","return",
        "var","seq","par","print","true","false","int","bool","string","c_channel",
        "break", "number", "in"}
    
    def __init__(self, text: str):
        self.text = text
        parts = []
        for name, regex in self.TOKEN_SPEC:
            parts.append(f"(?P<{name}>{regex})")
        self.master_re = re.compile("|".join(parts))
        self.line = 1
        self.col = 1

    def tokenize(self) -> List[Token]:
        tokens = []
        pos = 0
        while pos < len(self.text):
            m = self.master_re.match(self.text, pos)
            if not m:
                raise LexerError(f"Unexpected char {self.text[pos]!r} at {self.line}:{self.col}")
            kind = m.lastgroup
            val = m.group()
            if kind == "NEWLINE":
                self.line += 1
                self.col = 1
                pos = m.end()
                continue
            if kind == "SKIP" or kind == "COMMENT" or kind == "MULTICOMMENT": #multicomentarios e comentarios
                if kind == "MULTICOMMENT":
                    self.line += val.count('\n')
                    if val.count('\n') > 0:
                        self.col = len(val) - val.rfind('\n')
                    else:
                        self.col += len(val)
                else:
                    self.col += len(val)
                pos = m.end()
                continue
            start_col = self.col
            if kind == "ID" and val in self.KEYWORDS:
                kind = val.upper()
            tok = Token(kind, val, self.line, start_col)
            tokens.append(tok)
            pos = m.end()
            self.col += len(val)
        tokens.append(Token("EOF", "", self.line, self.col))
        return tokens
