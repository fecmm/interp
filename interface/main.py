from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


from minipar.lexer_251018_215612 import Lexer
from minipar.parser_251018_215706 import Parser

app = FastAPI()
templates = Jinja2Templates(directory="interface/templates")

app.mount("/static", StaticFiles(directory="interface/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/run", response_class=HTMLResponse)
def run_code(request: Request, code: str = Form(...)):
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse_program()
        result = str(ast)  # ou outra forma de visualizar o AST
        return templates.TemplateResponse("index.html", {"request": request, "result": result, "code": code})
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "result": f"Error: {e}", "code": code})

