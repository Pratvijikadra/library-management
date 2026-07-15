from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from backend.routes.auth import ensure_authenticated_user
from backend.database import books_collection
from fastapi import responses

router = APIRouter()

templates = Jinja2Templates(directory="frontend/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user_session=Depends(ensure_authenticated_user)
):

    if not user_session:
        return responses.RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # ===========================
    # Dashboard Statistics
    # ===========================

    total_books = books_collection.count_documents({})

    available_books = books_collection.count_documents({
        "status": "Available"
    })

    unavailable_books = books_collection.count_documents({
        "status": "Unavailable"
    })

    top_rated_books = books_collection.count_documents({
        "average_rating": {"$gte": 4}
    })

    # ===========================
    # Recently Added Books
    # ===========================

    latest_books = list(
        books_collection.find()
        .sort("created_at", -1)
        .limit(6)
    )

    # ===========================
    # Highest Rated Books
    # ===========================

    recommended_books = list(
        books_collection.find()
        .sort("average_rating", -1)
        .limit(6)
    )

    return templates.TemplateResponse(request,
        "index.html",
        {
            "request": request,
            "user": user_session,

            "stats": {
                "total_books": total_books,
                "available_books": available_books,
                "unavailable_books": unavailable_books,
                "top_rated_books": top_rated_books,
            },

            "latest_books": latest_books,

            "recommended_books": recommended_books
        }
    )