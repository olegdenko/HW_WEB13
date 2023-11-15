from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from libgravatar import Gravatar
import pathlib
from src.database.db import get_db
from src.routes import auth, notes, tags, contacts


app = FastAPI()

app.include_router(auth.router, prefix="/api")
# app.include_router(tags.router, prefix="/api")
# app.include_router(notes.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")

templates = Jinja2Templates(directory="src/templates")

app.mount("/static", StaticFiles(directory="src/static"), name="static")

favicon_path = pathlib.Path("src/favicon/favicon.ico")


@app.get("/favicon.ico", response_class=FileResponse)
def get_favicon():
    return favicon_path


@app.get("/", response_class=HTMLResponse, description="Main Page")
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html", {"request": request, "title": "My App"}
    )


@app.get("/login", response_class=HTMLResponse, description="Login")
async def login(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request, "title": "My App"}
    )


@app.get("/register", response_class=HTMLResponse, description="Sign Up")
async def register(request: Request):
    return templates.TemplateResponse(
        "register.html", {"request": request, "title": "My App"}
    )


@app.get("/api/healthchaker")
def healthchaker(db, Session=Depends(get_db)):
    return {"message": "Hello World"}


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="localhost", port="8000", reload=True)
