from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/src", StaticFiles(directory="src"), name="src")

templates = Jinja2Templates(directory="templates")

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}
    # return templates.TemplateResponse("home.html", {"request": request})

@app.get("/chart")
async def root(request: Request):
    return templates.TemplateResponse("chart1.html", {"request": request})

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("404.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/password-reset", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("password-reset.html", {"request": request})