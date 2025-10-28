# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
import os


from minipar.lexer_251018_215612 import Lexer
from minipar.parser_251018_215706 import Parser
from minipar.interpreter_3000 import Interpreter

app = FastAPI()


templates_path = os.path.join(os.path.dirname(__file__), "interface", "templates")
env = Environment(loader=FileSystemLoader(templates_path))


app.mount("/static", StaticFiles(directory=os.path.join("interface", "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def index():
    template = env.get_template("index.html")
    return template.render()

@app.post("/run", response_class=HTMLResponse)
async def run_code(code: str = Form(...)):
    try:
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()  

      
        parser = Parser(tokens)
        ast = parser.parse()  

      
        interpreter = Interpreter()
        output = interpreter.run(ast)  

    except Exception as e:
        output = f"Erro: {e}"

    template = env.get_template("index.html")
    return template.render(code=code, output=output)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
