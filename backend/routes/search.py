from fastapi import APIRouter, HTTPException,status, Query
from backend.schemas import Books
from backend.database import books_collection
from typing import List, Optional


router = APIRouter()

@router.get("/search-books", response_model=List[Books])
async def search_and_filter_books(
   
    search: Optional[str] = Query(None, description="Search by Title or ISBN"),
    
    # Filters for Dropdowns (IDs or Language)
    category_name: Optional[str] = Query(None, description="Filter by Category name"),
    author_name: Optional[str] = Query(None, description="Filter by Author name"),
    publisher_name: Optional[str] = Query(None, description="Filter by Publisher name"),
    language: Optional[str] = Query(None, description="Filter by Language (e.g., hindi, english)")
):
    try:
        # 1. Create empty query dictionary
        query = {}

        # 2. If the user has written something in Search, then match it in Title or ISBN (Case-Insensitive)
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"isbn": {"$regex": search, "$options": "i"}}
            ]

        # 3. Check the remaining filters and add them to the query
        if category_name is not None:
            query["category_name"] = category_name
            
        if author_name is not None:
            query["author_name"] = author_name
            
        if publisher_name is not None:
            query["publisher_name"] = publisher_name
            
        if language:
            # Exact language or with regex (like 'English' or 'english' both work)
            query["language"] = {"$regex": f"^{language}$", "$options": "i"}

        # 4. Find data from MongoDB
        books_cursor = books_collection.find(query)
        books_list = list(books_cursor)

        return books_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



