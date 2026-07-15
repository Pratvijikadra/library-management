from fastapi import APIRouter, HTTPException
from fastapi import Request
from fastapi import Depends
from fastapi import responses
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.database import (
    books_collection,
    issued_books_collection,
    wishlist_collection,
    reservations_collection
)

from backend.routes.auth import ensure_authenticated_user

from bson import ObjectId

from datetime import datetime, timezone



router = APIRouter()

templates = Jinja2Templates(directory="frontend/templates")



@router.get("/library", response_class=HTMLResponse)
async def my_library(
    request: Request,
    user_session=Depends(ensure_authenticated_user)
):

    if not user_session:
        return responses.RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    issued_cursor = issued_books_collection.find({
        "user_id": user_session["user_id"],
        "status": "Issued"
    }).sort("issue_date", -1)

    

    issued_books = []

    for issue in issued_cursor:

        book = books_collection.find_one({
            "_id": ObjectId(issue["book_id"])
        })

        if book:

            book["_id"] = str(book["_id"])

            issue["_id"] = str(issue["_id"])

            issue["book"] = book

            issued_books.append(issue)

    return templates.TemplateResponse(
        request,
        "library.html",
        {
            "request": request,
            "user": user_session,
            "issued_books": issued_books,
            "now": datetime.now(timezone.utc).replace(tzinfo=None)
        }
    )




@router.get("/library/return/{issue_id}")
async def return_book(
    issue_id: str,
    user_session=Depends(ensure_authenticated_user)
):

    if not user_session:
        return responses.RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    issue = issued_books_collection.find_one({
        "_id": ObjectId(issue_id),
        "user_id": user_session["user_id"],
        "status": "Issued"
    })

    if not issue:
        raise HTTPException(
            status_code=404,
            detail="Issued book not found."
        )

    # Book stock increase
    books_collection.update_one(
        {
            "_id": ObjectId(issue["book_id"])
        },
        {
            "$inc": {
                "available_copies": 1
            }
        }
    )

    # Update issued record
    issued_books_collection.update_one(
        {
            "_id": ObjectId(issue_id)
        },
        {
            "$set": {
                "status": "Returned",
                "return_date": datetime.now(timezone.utc)
            }
        }
    )

    return responses.RedirectResponse(
        url="/library",
        status_code=status.HTTP_303_SEE_OTHER
    )