from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from minipar.interpreter_3000 import Interpreter
from minipar.parser_251018_215706 import parse  

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": ""})


@app.post("/run", response_class=HTMLResponse)
async def run_code(request: Request, code: str = Form(...)):
    try:
        # parse retorna a AST do código MiniPar
        ast = parse(code)
        interpreter = Interpreter()
        interpreter.interpret(ast)
        output = "Código executado com sucesso."
    except Exception as e:
        output = f"Erro: {str(e)}"

    return templates.TemplateResponse("index.html", {"request": request, "result": output})
