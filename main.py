from fastapi import FastAPI
from backend.database import users_collection
from backend.routes import books, search, admin, auth
from fastapi.responses import HTMLResponse
from fastapi import Request, HTTPException, Form, Response, responses, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.routes.auth import ensure_authenticated_user
from fastapi import status







app = FastAPI()

app.include_router(books.router)
app.include_router(search.router)
app.include_router(admin.router)
app.include_router(auth.router)




app.mount("/static", StaticFiles(directory="frontend"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, user_session = Depends(ensure_authenticated_user)):
    if not user_session:
        return responses.RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request,"index.html", {"request": request, "user":user_session})

    




