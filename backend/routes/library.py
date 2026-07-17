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

    wishlist_cursor = wishlist_collection.find(
    {
        "user_id": user_session["user_id"]
    }
    ).sort("created_at", -1)

    wishlist = []

    for item in wishlist_cursor:

        book = books_collection.find_one(
            {
                "_id": ObjectId(item["book_id"])
            }
        )

        if book:

            book["_id"] = str(book["_id"])

            item["_id"] = str(item["_id"])

            item["book"] = book

            wishlist.append(item)


    reservation_cursor = reservations_collection.find(
    {
        "user_id": user_session["user_id"],
        "status": "Reserved"
    }
    ).sort("reserved_at", -1)

    reservations = []

    for reservation in reservation_cursor:

        book = books_collection.find_one(
            {
                "_id": ObjectId(reservation["book_id"])
            }
        )

        if book:

            reservation["_id"] = str(reservation["_id"])
            book["_id"] = str(book["_id"])

            reservation["book"] = book

            reservations.append(reservation)

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    for issue in issued_cursor:

        book = books_collection.find_one({
            "_id": ObjectId(issue["book_id"])
        })

        if book:

            book["_id"] = str(book["_id"])

            issue["_id"] = str(issue["_id"])

            issue["book"] = book

            if "due_date" in issue and issue["due_date"]:
                try:
                    due_date = issue["due_date"].replace(tzinfo=None)
                    delta = now - due_date
                    issue["overdue_days"] = max(0, delta.days)
                    issue["fine"] = issue["overdue_days"] * 5
                    issue["fine_amount"] = issue["fine"]
                    # Update database with the calculated fine
                    issued_books_collection.update_one(
                        {"_id": ObjectId(issue["_id"])},
                        {"$set": {"fine_amount": issue["fine_amount"]}}
                    )
                except Exception:
                    issue["overdue_days"] = 0
                    issue["fine"] = 0
                    issue["fine_amount"] = 0
            else:
                issue["overdue_days"] = 0
                issue["fine"] = 0
                issue["fine_amount"] = 0

            issued_books.append(issue)

    # reading history
    history_cursor = issued_books_collection.find(
    {
        "user_id": user_session["user_id"],
        "status": "Returned"
    }
    ).sort("return_date", -1)

    reading_history = []

    for history in history_cursor:

        book = books_collection.find_one(
            {
                "_id": ObjectId(history["book_id"])
            }
        )

        if book:

            history["_id"] = str(history["_id"])
            book["_id"] = str(book["_id"])

            history["book"] = book
            history["fine_amount"] = history.get("fine_amount", 0)

            reading_history.append(history)
    

    return templates.TemplateResponse(
        request,
        "library.html",
        {
            "request": request,
            "user": user_session,
            "issued_books": issued_books,
            "wishlist": wishlist,
            "reading_history": reading_history,
            "reservations": reservations,
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


    fine = 0
    overdue_days = 0

    if issue.get("due_date"):
        try:
            now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
            due_naive = issue["due_date"].replace(tzinfo=None)
            
            if now_naive > due_naive:
                overdue_days = (now_naive - due_naive).days
        except Exception:
            pass

    fine = overdue_days * 5
    # Update issued record
    issued_books_collection.update_one(
        {
            "_id": ObjectId(issue_id)
        },
        {
            "$set": {
                "status": "Returned",
                "return_date": datetime.now(timezone.utc),
                "fine_amount":fine
            }
        }
    )

    return responses.RedirectResponse(
        url="/library",
        status_code=status.HTTP_303_SEE_OTHER
    )



# add to wishlist
@router.get("/wishlist/add/{book_id}")
async def add_to_wishlist(
    book_id: str,
    user_session=Depends(ensure_authenticated_user)
):

    if not user_session:
        return responses.RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    book = books_collection.find_one(
        {
            "_id": ObjectId(book_id)
        }
    )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found."
        )

    exists = wishlist_collection.find_one(
        {
            "user_id": user_session["user_id"],
            "book_id": book_id
        }
    )

    if exists:
        return responses.RedirectResponse(
            url=f"/books/{book_id}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    wishlist_collection.insert_one(
        {
            "user_id": user_session["user_id"],
            "book_id": book_id,
            "created_at": datetime.now(timezone.utc)
        }
    )

    return responses.RedirectResponse(
        url=f"/books/{book_id}",
        status_code=status.HTTP_303_SEE_OTHER
    )



# remove wishlist
@router.get("/wishlist/remove/{wishlist_id}")
async def remove_wishlist(
    wishlist_id: str,
    user_session=Depends(ensure_authenticated_user)
):

    if not user_session:
        return responses.RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    wishlist_collection.delete_one(
        {
            "_id": ObjectId(wishlist_id),
            "user_id": user_session["user_id"]
        }
    )

    return responses.RedirectResponse(
        url="/library/",
        status_code=status.HTTP_303_SEE_OTHER
    )



# reservation API
@router.get("/reservation/add/{book_id}")
async def reserve_book(
    book_id: str,
    user_session=Depends(ensure_authenticated_user)
):

    if not user_session:
        return responses.RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Book exists?
    book = books_collection.find_one(
        {
            "_id": ObjectId(book_id)
        }
    )

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found."
        )

    # Book available -> don't allow reservation
    if book["available_copies"] > 0:
        raise HTTPException(
            status_code=400,
            detail="Book is available. Please issue it instead."
        )

    # Already reserved?
    exists = reservations_collection.find_one(
        {
            "user_id": user_session["user_id"],
            "book_id": book_id,
            "status": "Reserved"
        }
    )

    if exists:
        raise HTTPException(
            status_code=400,
            detail="You have already reserved this book."
        )

    # Already issued?
    already_issued = issued_books_collection.find_one(
        {
            "user_id": user_session["user_id"],
            "book_id": book_id,
            "status": "Issued"
        }
    )

    if already_issued:
        raise HTTPException(
            status_code=400,
            detail="You have already issued this book."
        )

    reservations_collection.insert_one(
        {
            "user_id": user_session["user_id"],
            "book_id": book_id,
            "reserved_at": datetime.now(timezone.utc),
            "status": "Reserved"
        }
    )

    return responses.RedirectResponse(
        url="/library",
        status_code=status.HTTP_303_SEE_OTHER
    )



# cancel reservation api
@router.get("/reservation/cancel/{reservation_id}")
async def cancel_reservation(
    reservation_id: str,
    user_session=Depends(ensure_authenticated_user)
):

    if not user_session:
        return responses.RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    reservations_collection.delete_one(
        {
            "_id": ObjectId(reservation_id),
            "user_id": user_session["user_id"]
        }
    )

    return responses.RedirectResponse(
        url="/library",
        status_code=status.HTTP_303_SEE_OTHER
    )