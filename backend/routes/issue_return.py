from fastapi import APIRouter, HTTPException,status, Request, Depends
from backend.schemas import Books, CategorySchema, LanguageSchema
from backend.database import books_collection, categories_collection, languages_collection, issued_books_collection, users_collection
from typing import List, Dict, Any
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from fastapi import Query
from backend.routes.auth import ensure_authenticated_user
from fastapi import responses



router = APIRouter()


router.mount("/static", StaticFiles(directory="frontend"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


# @router.get("/issue-return", response_class=HTMLResponse)
# async def issue_return(request: Request, user=Depends(ensure_authenticated_user)):
#     if not user:
#         return responses.RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
#     return templates.TemplateResponse(request, "issue_return.html", {"request": request, "user": user})



@router.get("/issue-return", response_class=HTMLResponse)
async def issue_return(request: Request, user=Depends(ensure_authenticated_user)):
    if not user:
        return responses.RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # MongoDB Aggregation Pipeline: issued_books ko users aur books collection ke sath join karne ke liye
    pipeline = [
        {
            # user_id string ko ObjectId me convert karke users_collection se join karein
            "$addFields": {
                "user_obj_id": { "$toObjectId": "$user_id" },
                "book_obj_id": { "$toObjectId": "$book_id" }
            }
        },
        {
            "$lookup": {
                "from": "users",  # users collection ka naam (database.py ke mutabik check kar lena)
                "localField": "user_obj_id",
                "foreignField": "_id",
                "as": "user_info"
            }
        },
        {
            "$lookup": {
                "from": "books",  # books collection ka naam
                "localField": "book_obj_id",
                "foreignField": "_id",
                "as": "book_info"
            }
        },
        {
            # Array ko flat object me convert karne ke liye
            "$unwind": { "path": "$user_info", "preserveNullAndEmptyArrays": True }
        },
        {
            "$unwind": { "path": "$book_info", "preserveNullAndEmptyArrays": True }
        },
        {
            # Data sorting: Newest issues pahle dikhein
            "$sort": { "issue_date": -1 }
        }
    ]
    
    raw_records = issued_books_collection.aggregate(pipeline).to_list(length=1000)
    
    # Data Formatting (Dates ko clean string me convert karna aur safely nested values nikalna)
    records = []
    for record in raw_records:
        user_data = record.get("user_info", {})
        book_data = record.get("book_info", {})
        
        # Date helper function
        def format_date(dt):
            if isinstance(dt, datetime):
                return dt.strftime("%Y-%m-%d %H:%M")
            return dt if dt else "N/A"

        records.append({
            "id": str(record["_id"]),
            "user_name": user_data.get("name", "Unknown User"),
            "user_email": user_data.get("email", "N/A"),
            "book_title": book_data.get("title", "Unknown Book"),
            "issue_date": format_date(record.get("issue_date")),
            "due_date": format_date(record.get("due_date")),
            "return_date": format_date(record.get("return_date")) if record.get("return_date") else "-",
            "status": record.get("status", "Issued"),
            "fine_amount": record.get("fine_amount", 0),
            "fine_paid": record.get("fine_paid", False)
        })

    return templates.TemplateResponse(request, "issue_return.html", {
        "request": request, 
        "user": user,
        "records": records  # Yeh data HTML me pass hoga
    })