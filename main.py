from fastapi import FastAPI
from backend.database import users_collection
from backend.routes import books, search
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()

app.include_router(books.router)
app.include_router(search.router)




app.mount("/static", StaticFiles(directory="frontend"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


@app.get("/")
async def root():
    return {"message": "Library system works"}



    




