from fastapi import APIRouter, HTTPException, status, Response, BackgroundTasks, Depends, Request
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from backend.database import db, users_collection, books_collection, categories_collection, languages_collection, otps_collection
from backend.schemas import Books, CategorySchema, LanguageSchema
import os
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse


router = APIRouter()

router.mount("/static", StaticFiles(directory="frontend"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# --- Configuration Setup ---
# SECRET_KEY = os.getenv("JWT_SECRET_KEY", "YOUR_SUPER_SECURE_RANDOM_SECRET_KEY_98765")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 120  # Token session duration configurations


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing! Production deployment halted.")


# Custom dependency to enforce authentication on HTML page routes
async def ensure_authenticated_user(request: Request):
    """
    Checks if a valid user access session token is present.
    If not authenticated, aborts the flow and redirects to the login gateway.
    """
    # 1. Look for token inside HTTP Cookies (Best practice for HTML rendering)
    token = request.cookies.get("user_access_token")
    
    # 2. Fallback: check Authorization header if cookie isn't populated yet
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        # User is not logged in -> Throw redirect exception or return redirection directly
        return None
        
    try:
        # Decode the token array safely using your secret key configurations
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Returns user payload like user_id, email, etc.
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

print(f"Algorithm loaded successfully: {ALGORITHM}")

# --- Pydantic Schema Declarations ---
class UserRegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str





@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    try:
       
        
        return templates.TemplateResponse(
            request,
            "register.html", 
            {"request": request}
        )
    except Exception as e:
        print("ERROR:", str(e)) # Apne terminal logs me error dekhne ke liye
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    try:
       
        
        return templates.TemplateResponse(
            request,
            "login.html", 
            {"request": request}
        )
    except Exception as e:
        print("ERROR:", str(e)) # Apne terminal logs me error dekhne ke liye
        raise HTTPException(status_code=500, detail=str(e))

# --- Cryptography Helpers ---
def hash_password(password: str) -> str:
    """ Generates a secure salt and hashes the plain text password. """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ Compares secure hash against incoming plain text password mutation. """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    """ Encodes user session records into a signed compact JWT payload. """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS")))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Operational Endpoints ---

@router.post("/api/auth/register", status_code=201)
async def register_user(user_data: UserRegisterSchema):
    try:
        # Check case-insensitive email existence query check inside MongoDB
        existing_user = users_collection.find_one({"email": {"$regex": f"^{user_data.email}$", "$options": "i"}})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="An account with this email address already exists!"
            )
        
        # Safe password transformation mutation execution
        hashed_pw = hash_password(user_data.password)
        
        # Build document structure mapping configuration
        user_document = {
            "name": user_data.name,
            "email": user_data.email.lower().strip(),
            "password": hashed_pw,
            "created_at": datetime.now(timezone.utc)
        }
        
        users_collection.insert_one(user_document)
        return {"message": "Account created successfully! Redirecting to login page..."}

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database operational failure: {str(e)}")


@router.post("/api/auth/login")
async def login_user(credentials: UserLoginSchema):
    try:
        # Scan collection payload for exact match logs
        user = users_collection.find_one({"email": credentials.email.lower().strip()})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials! No registered account found with this email."
            )
        
        # Confirm password match hash validations
        if not verify_password(credentials.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials! The password entered is incorrect."
            )
        
        # Construct authorization response object mapping token
        token_payload = {"user_id": str(user["_id"]), "email": user["email"], "name": user["name"]}
        access_token = create_access_token(token_payload)
        
        return {
            "message": f"Welcome back, {user['name']}! Login successful.",
            "access_token": access_token,
            "token_type": "bearer"
        }

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication runtime issue: {str(e)}")



