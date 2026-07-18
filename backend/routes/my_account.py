from fastapi import APIRouter, Request, Depends, status, responses, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form
from fastapi.responses import RedirectResponse
from bson import ObjectId
from backend.database import users_collection
from backend.routes.auth import ensure_authenticated_user
from fastapi import Query
from fastapi import Form, HTTPException
from backend.routes.auth import verify_password, hash_password, create_access_token

router = APIRouter()

templates = Jinja2Templates(directory="frontend/templates")


@router.get("/account", response_class=HTMLResponse)
async def my_account(
    request: Request,
    success: str = Query(default=""),
    error: str = Query(default=""),
    user_session=Depends(ensure_authenticated_user)
):

    if not user_session:
        return responses.RedirectResponse(
            "/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    user = users_collection.find_one(
        {
            "email": user_session["email"]
        }
    )

    return templates.TemplateResponse(
        request,
        "my_account.html",
        {
            "request": request,
            "user": user_session,
            "profile": user,
            "success": success,
            "error": error
        }
    )




# update profile
@router.post("/account/update")
async def update_profile(
    response: Response,
    name: str = Form(...),
    email: str = Form(...),
    user_session=Depends(ensure_authenticated_user)
):

    # Email already exists?
    existing = users_collection.find_one({
        "email": email.lower().strip(),
        "_id": {
            "$ne": ObjectId(user_session["user_id"])
        }
    })

    if existing:
        return RedirectResponse(
            "/account?error=email_exists",
            status_code=303
        )

    users_collection.update_one(
        {
            "_id": ObjectId(user_session["user_id"])
        },
        {
            "$set": {
                "name": name.strip(),
                "email": email.lower().strip()
            }
        }
    )

    # Create new token
    token_payload = {
        "user_id": user_session["user_id"],
        "name": name.strip(),
        "email": email.lower().strip()
    }

    access_token = create_access_token(token_payload)

    redirect = RedirectResponse(
        "/account?success=profile_updated",
        status_code=303
    )

    redirect.set_cookie(
        key="user_access_token",
        value=access_token,
        httponly=False,
        samesite="strict",
        path="/"
    )

    return redirect

# change password

@router.post("/account/change-password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    user_session=Depends(ensure_authenticated_user)
):

    # Current user
    user = users_collection.find_one(
        {
            "email": user_session["email"]
        }
    )

    if not user:
        return RedirectResponse(
            "/account?error=user_not_found",
            status_code=303
        )

    # Verify current password
    if not verify_password(current_password, user["password"]):
        return RedirectResponse(
            "/account?error=wrong_password",
            status_code=303
        )

    # Password match
    if new_password != confirm_password:
        return RedirectResponse(
            "/account?error=password_mismatch",
            status_code=303
        )

    # Same password
    if verify_password(new_password, user["password"]):
        return RedirectResponse(
            "/account?error=same_password",
            status_code=303
        )

    # Update password
    users_collection.update_one(
        {
            "_id": user["_id"]
        },
        {
            "$set": {
                "password": hash_password(new_password)
            }
        }
    )

    return RedirectResponse(
        "/account?success=password_changed",
        status_code=303
    )