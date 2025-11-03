from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from minipar.lexer_251018_215612 import Lexer
from minipar.parser_251018_215706 import Parser
from minipar.interpreter_3000 import Interpreter

import io
import sys

app = FastAPI()
templates = Jinja2Templates(directory="interface/templates")
app.mount("/static", StaticFiles(directory="interface/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "code": "", "exec_result": "", "ast_result": ""},
    )


@app.post("/run", response_class=HTMLResponse)
def run_code(request: Request, code: str = Form(...)):
    try:
        # Lexing
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        # Parsing
        parser = Parser(tokens)
        ast = parser.parse_program()
        def format_ast(ast_obj):
            return str(ast_obj).replace("),", "),\n")  # ajusta conforme seu AST

        ast_output = format_ast(ast)
        # Interpretação
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            interpreter = Interpreter()
            interpreter.interpret(ast)
            exec_output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "code": code,
                "exec_result": exec_output,
                "ast_result": ast_output,
            },
        )

    except Exception as e:
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "code": code,
                "exec_result": f"Erro: {e}",
                "ast_result": f"Erro: {e}",
            },
        )


