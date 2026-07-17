from fastapi import APIRouter, HTTPException,status, Request
from backend.schemas import Books, CategorySchema, LanguageSchema
from backend.database import books_collection, categories_collection, languages_collection, issued_books_collection, users_collection
from typing import List, Dict, Any
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from fastapi import Query
from math import ceil




router = APIRouter()


router.mount("/static", StaticFiles(directory="frontend"), name="static")
templates = Jinja2Templates(directory="frontend/templates")









@router.post("/add-book")
async def add_book(book_data: Books):
    try:

        existing_book = books_collection.find_one({
            "isbn": {"$regex": f"^{book_data.isbn}$", "$options": "i"}
        })
    
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this ISBN already exists!"
            )
        # 1. 📂 Category Foreign Key Validation (Case-Insensitive)
        # Checking if this category exists in our categories collection
        category_exists = categories_collection.find_one({
            "name": {"$regex": f"^{book_data.category_name}$", "$options": "i"}
        })
        
        if not category_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{book_data.category_name}' is not available. Please add it to the category list first."
            )

        # 2. 🗣️ Language Foreign Key Validation (Case-Insensitive)
        # Checking if this language exists in our languages collection
        language_exists = languages_collection.find_one({
            "name": {"$regex": f"^{book_data.language}$", "$options": "i"}
        })
        
        if not language_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Language '{book_data.language}' is not available. Please choose a valid language."
            )

        # 3. Convert data to database format (JSON/Dict)
        book_dict = book_data.model_dump(mode="json")
        
        # Normalize names to match exact database casing
        book_dict["category_name"] = category_exists["name"]
        book_dict["language"] = language_exists["name"]
        if not book_dict.get("created_at"):
            book_dict["created_at"] = datetime.now().isoformat()
        book_dict["updated_at"] = datetime.now().isoformat()

        # 4. Insert book into database and return a clean response for the JavaScript Toast
        result = books_collection.insert_one(book_dict)
        
        # Convert internal MongoDB ObjectId to a string to prevent JSON serialization errors
        if "_id" in book_dict:
            book_dict["_id"] = str(result.inserted_id)

        # Return a custom success dict instead of the raw schema model
        return {
            "status": "success",
            "message": f"'{book_dict['title']}' has been added successfully!",
            "data": book_dict
        }

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-all-books", response_model=list[Books])
async def get_all_books():
    try:
        return list(books_collection.find())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-book", response_model=Books)
async def get_book(isbn: str):
    try:
        return books_collection.find_one({"isbn": isbn})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update-book/{isbn}", response_model=Books)
async def update_book(isbn: str, books: Books):
    try:
        # Pehle check karein ki book exist karti hai ya nahi
        existing_book = books_collection.find_one({"isbn": isbn})
        if not existing_book:
            raise HTTPException(status_code=404, detail="Book not found with this ISBN")
            
        # Update logic
        books_collection.update_one({"isbn": isbn}, {"$set": books.model_dump(mode="json")})
        
        # Updated data return karein
        updated_book = books_collection.find_one({"isbn": isbn})
        return updated_book
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-book/{isbn}")
async def delete_book(isbn: str):
    try:
        existing_book = books_collection.find_one({"isbn": isbn})
        if not existing_book:
            raise HTTPException(status_code=404, detail="Book not found with this ISBN")            
   
        books_collection.delete_one({"isbn": isbn})
     
        return {
            "title": existing_book.get('title', 'Unknown'),
            "status": "deleted successfully"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# MongoDB Helper: ObjectId ko String me convert karne ke liye helper function
def category_helper(category) -> dict:
    return {
        "id": str(category["_id"]),
        "name": category["name"],
        "description": category.get("description", "")  # description field ko bhi secure kiy
    }

def language_helper(language):
    return{
        "id":str(language["_id"]),
        "name":language["name"]
    }



@router.get("/categories", response_class=HTMLResponse)
async def categories_page(request: Request):
    try:
        cursor = categories_collection.find({}).sort("name", 1)
        categories = [category_helper(cat) for cat in cursor]
        
        return templates.TemplateResponse(
            request,
            "manage_categories.html", 
            {"request": request, "categories": categories}
        )
    except Exception as e:
        print("ERROR:", str(e)) # Apne terminal logs me error dekhne ke liye
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/categories")
async def get_all_categories():
    try:
        # Pura data find kiya aur name ke according sort kiya (A to Z)
        cursor = categories_collection.find({}).sort("name", 1)
        categories = [category_helper(cat) for cat in cursor]
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-category", response_model=dict, status_code=201)
async def add_category(category: CategorySchema):
    try:
        # Check duplicate category name (case-insensitive)
        exists = categories_collection.find_one({"name": {"$regex": f"^{category.name}$", "$options": "i"}})
        if exists:
            raise HTTPException(status_code=400, detail="Category already exists!")
        
        categories_collection.insert_one({"name": category.name})
        return {"message": f"Category '{category.name}' added successfully"}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 3. 📝 UPDATE CATEGORY (Inline Edit Handle karne ke liye)
@router.put("/update-category/{category_id}", response_model=dict)
async def update_category(category_id: str, category: CategorySchema):
    try:
        if not ObjectId.is_valid(category_id):
            raise HTTPException(status_code=400, detail="Invalid Category ID format")
            
        # Check duplicate name: jis category ko badal rahe hain uske alawa kisi aur ka same name na ho
        exists = categories_collection.find_one({
            "_id": {"$ne": ObjectId(category_id)},
            "name": {"$regex": f"^{category.name}$", "$options": "i"}
        })
        if exists:
            raise HTTPException(status_code=400, detail="Another category with this name already exists!")

        result = categories_collection.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": {
                "name": category.name
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Category not found!")
            
        return {"message": "Category updated cleanly in real-time!"}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 4. 🗑️ DELETE CATEGORY (Aapki unique requirement)
@router.delete("/delete-category/{category_id}", response_model=dict)
async def delete_category(category_id: str):
    try:
        # Pehle check karein ki id valid MongoDB ObjectId hai ya nahi
        if not ObjectId.is_valid(category_id):
            raise HTTPException(status_code=400, detail="Invalid Category ID format")
            
        # Database se delete karein
        result = categories_collection.delete_one({"_id": ObjectId(category_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Category not found or already deleted!")
            
        return {"message": "Category record removed successfully."}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== LANGUAGE APIS ====================




@router.get("/languages", response_class=HTMLResponse)
async def languages_page(request: Request):
    try:
        cursor = languages_collection.find({}).sort("name", 1)
        languages = [language_helper(lang) for lang in cursor]
        
        return templates.TemplateResponse(
            request,
            "manage_languages.html", 
            {"request": request, "languages": languages}
        )
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/languages", response_model=List[LanguageSchema])
async def get_all_languages():
    try:
        cursor = languages_collection.find({}).sort("name", 1)
        languages = [language_helper(lang) for lang in cursor]
        return languages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-language", response_model=dict, status_code=201)
async def add_language(language: LanguageSchema):
    try:
        # check if language is available or not
        exists = languages_collection.find_one({"name": {"$regex": f"^{language.name}$", "$options": "i"}})
        if exists:
            raise HTTPException(status_code=400, detail="Language already exists!")
        
        languages_collection.insert_one({"name": language.name})
        return {"message": f"Language '{language.name}' added successfully"}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






        

@router.put("/update-language/{language_id}", response_model=dict)
async def update_language(language_id: str, language: LanguageSchema):
    try:
        if not ObjectId.is_valid(language_id):
            raise HTTPException(status_code=400, detail="Invalid Language ID format")
            
        # Check duplicate name: jis language ko badal rahe hain uske alawa kisi aur ka same name na ho
        exists = languages_collection.find_one({
            "_id": {"$ne": ObjectId(language_id)},
            "name": {"$regex": f"^{language.name}$", "$options": "i"}
        })
        if exists:
            raise HTTPException(status_code=400, detail="Another language with this name already exists!")

        result = languages_collection.update_one(
            {"_id": ObjectId(language_id)},
            {"$set": {
                "name": language.name
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Language not found!")
            
        return {"message": "Language updated cleanly in real-time!"}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






@router.delete("/delete-language/{language_id}", response_model=dict)
async def delete_language(language_id: str):
    try:
        if not ObjectId.is_valid(language_id):
            raise HTTPException(status_code=400, detail="Invalid Language ID format")
            
        result = languages_collection.delete_one({"_id": ObjectId(language_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Language not found or already deleted!")
            
        return {"message": "Language record removed successfully."}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







@router.get("/manage-books", response_class=HTMLResponse)
async def get_manage_books_page(request: Request):
    try:
        # 1. Fetch all books from MongoDB
        books_cursor = books_collection.find({})
        books_list = []
        for book in books_cursor:
            if "_id" in book:
                book["_id"] = str(book["_id"])  # Convert ObjectId to string for JSON/Jinja compatibility
            books_list.append(book)
            
        # 2. Fetch allowed Categories and Languages for the Add Book dropdowns
        categories_cursor = categories_collection.find({}, {"_id": 0})
        languages_cursor = languages_collection.find({}, {"_id": 0})
        
        categories_list = list(categories_cursor)
        languages_list = list(languages_cursor)
        
        # 3. Render page with latest FastAPI syntax using request as the first argument
        return templates.TemplateResponse(
            request, 
            "manage_book.html", 
            {
                "request": request, 
                "books": books_list,
                "categories": categories_list,
                "languages": languages_list
            }
        )

    except Exception as e:
        import traceback
        print("--- ACTUAL ERROR TRACEBACK ---")
        traceback.print_exc()  # Prints the full stack trace to the console for debugging
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)







# pyrefly: ignore [missing-import]
from fastapi import Depends, Query, status, responses
from backend.routes.auth import ensure_authenticated_user



# ==========================================================
# MEMBER - Browse Books
# ==========================================================

@router.get("/books", response_class=HTMLResponse)
async def browse_books(
    request: Request,
    user_session=Depends(ensure_authenticated_user),

    search: str = Query(default=""),

    category: str = Query(default=""),

    language: str = Query(default=""),

    sort: str = Query(default="latest"),

    page: int = Query(default=1, ge=1),

    limit: int = Query(default=12, ge=1)
):


    if not user_session:
        return responses.RedirectResponse(
        url="/login",
        status_code=status.HTTP_303_SEE_OTHER
    )



    try:

        query = {}

        # -----------------------------
        # Search
        # -----------------------------

        if search:

            query["$or"] = [

                {
                    "title": {
                        "$regex": search,
                        "$options": "i"
                    }
                },

                {
                    "author_name": {
                        "$regex": search,
                        "$options": "i"
                    }
                },

                {
                    "isbn": {
                        "$regex": search,
                        "$options": "i"
                    }
                }

            ]

        # -----------------------------
        # Category
        # -----------------------------

        if category:

            query["category_name"] = category

        # -----------------------------
        # Language
        # -----------------------------

        if language:

            query["language"] = language

        # -----------------------------
        # Sorting
        # -----------------------------

        sort_query = [("created_at", -1)]

        if sort == "oldest":

            sort_query = [("created_at", 1)]

        elif sort == "title":

            sort_query = [("title", 1)]

        elif sort == "title_desc":

            sort_query = [("title", -1)]

        elif sort == "rating":

            sort_query = [("average_rating", -1)]

        # -----------------------------
        # Pagination
        # -----------------------------

        total_books = books_collection.count_documents(query)

        total_pages = ceil(total_books / limit) if total_books else 1

        skip = (page - 1) * limit

        cursor = (

            books_collection.find(query)

            .sort(sort_query)

            .skip(skip)

            .limit(limit)

        )

        books = []

        for book in cursor:

            book["_id"] = str(book["_id"])

            books.append(book)

        categories = list(

            categories_collection.find({}, {"_id": 0})

            .sort("name", 1)

        )

        languages = list(

            languages_collection.find({}, {"_id": 0})

            .sort("name", 1)

        )

        return templates.TemplateResponse(

            request,

            "books.html",

            {

                "request": request,
                "user":user_session,

                "books": books,

                "categories": categories,

                "languages": languages,

                "current_page": page,

                "total_pages": total_pages,

                "search": search,

                "selected_category": category,

                "selected_language": language,

                "selected_sort": sort,

                "total_books": total_books

            }

        )

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )






@router.get("/books/{book_id}", response_class=HTMLResponse)
async def book_details(
    request: Request,
    book_id: str,
    user_session=Depends(ensure_authenticated_user)
):

    if not user_session:
        return responses.RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:

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

        book["_id"] = str(book["_id"])

        related_books = list(

            books_collection.find(
                {
                    "category_name": book["category_name"],
                    "_id": {
                        "$ne": ObjectId(book_id)
                    }
                }
            )

            .limit(4)

        )

        for item in related_books:
            item["_id"] = str(item["_id"])

        has_issued = issued_books_collection.find_one({
            "book_id": book_id,
            "user_id": user_session["user_id"],
            "status": "Issued"
        }) is not None

        return templates.TemplateResponse(

            request,

            "book_detail.html",

            {

                "request": request,

                "user": user_session,

                "book": book,

                "related_books": related_books,
                
                "has_issued": has_issued

            }

        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )



@router.get("/books/{book_id}/issue")
async def issue_book(

    book_id:str,

    user_session=Depends(ensure_authenticated_user)

):

    if not user_session:

        return responses.RedirectResponse(

            url="/login",

            status_code=status.HTTP_303_SEE_OTHER

        )

    book=books_collection.find_one(

        {

            "_id":ObjectId(book_id)

        }

    )

    if not book:

        raise HTTPException(

            status_code=404,

            detail="Book not found."

        )

    if book["available_copies"]<=0:

        raise HTTPException(

            status_code=400,

            detail="Book not available."

        )

    already=issued_books_collection.find_one(

        {

            "book_id":book_id,

            "user_id":user_session["user_id"],

            "status":"Issued"

        }

    )

    if already:

        raise HTTPException(

            status_code=400,

            detail="Book already issued."

        )

    issue_date=datetime.now(timezone.utc)

    due_date=issue_date+timedelta(days=15)

    issued_books_collection.insert_one(

        {

            "user_id":user_session["user_id"],

            "book_id":book_id,

            "issue_date":issue_date,

            "due_date":due_date,

            "return_date":None,

            "status":"Issued",
            "fine_amount": 0,
            "fine_paid": False

        }

    )

    books_collection.update_one(

        {

            "_id":ObjectId(book_id)

        },

        {

            "$inc":{

                "available_copies":-1

            }

        }

    )

    return responses.RedirectResponse(

        url="/library",

        status_code=status.HTTP_303_SEE_OTHER

    )






@router.get("/members")
async def members(
    request: Request,
    user_session=Depends(ensure_authenticated_user)
):

    if not user_session:
        return responses.RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )


    users = list(users_collection.find({}))

    for user in users:
        user["_id"] = str(user["_id"])

    return templates.TemplateResponse(
        request,
        "members.html",
        {
            "request": request,
            "users": users
        }
    )


@router.delete("/delete-user/{user_id}")
async def delete_user(
    user_id: str,
    user_session=Depends(ensure_authenticated_user)
):

    if not user_session:
        return responses.RedirectResponse(
            url="/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    user = users_collection.find_one(
        {
            "_id": ObjectId(user_id)
        }
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    users_collection.delete_one(
        {
            "_id": ObjectId(user_id)
        }
    )

    return responses.RedirectResponse(
        url="/members",
        status_code=status.HTTP_303_SEE_OTHER
    )