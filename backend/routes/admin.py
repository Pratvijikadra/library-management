from backend.database import users_collection
import os
import random
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from fastapi import Request, HTTPException, Form, responses, APIRouter, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from backend.database import otps_collection, books_collection, categories_collection, issued_books_collection


load_dotenv()

# Admin credentials load from env
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")



# Temporary OTP Storage (Production me Redis ya database behtar hota hai, par abhi runtime memory me save karenge)
# Format: {"otp": "123456", "verified_email": False}
admin_session_state = {}

# Yeh line ensure karegi ki 'created_at' time ke exact 300 seconds (5 mins) baad document automatic delete ho jaye
otps_collection.create_index("created_at", expireAfterSeconds=300)



# Email Sending Utility Function
def send_otp_email(to_email: str, otp_code: str):
    msg = MIMEText(f"Your Library Management System Admin Verification OTP code is: {otp_code}. It is valid for 5 minutes.")
    msg['Subject'] = 'Admin Login Verification OTP'
    msg['From'] = os.getenv("MAIL_USERNAME")
    msg['To'] = to_email

    with smtplib.SMTP(os.getenv("MAIL_SERVER"), int(os.getenv("MAIL_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))
        server.sendmail(os.getenv("MAIL_USERNAME"), to_email, msg.as_string())


router = APIRouter()


router.mount("/static", StaticFiles(directory="frontend"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


# 1. Login Page Render karna
@router.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request):

    return templates.TemplateResponse(
        request, 
        "admin_login.html", 
        {"request": request, "error": None}
    )





from datetime import datetime, timezone

@router.post("/admin/login")
async def handle_admin_login(request: Request, email: str = Form(...), password: str = Form(...)):
    if email != ADMIN_EMAIL or password != ADMIN_PASSWORD:
        return templates.TemplateResponse(request, "admin_login.html", {"request": request, "error": "Invalid Email or Password!"})
    
    try:
        # 1. Secure 6-Digit OTP generate kiya
        otp = str(random.randint(100000, 999999))
        
        # 2. Pehle se maujud koi purana OTP ho toh use clear kar dein
        otps_collection.delete_many({"email": email})
        
        # 3. MongoDB me data insert karein (created_at field lagana zaroori hai TTL ke liye)
        otps_collection.insert_one({
            "email": email,
            "otp": otp,
            "verified_email": True,
            "created_at": datetime.now(timezone.utc)  # UTC time lagana compulsory hai MongoDB TTL ke liye
        })
        
        # 4. Email send call
        send_otp_email(email, otp)
        
        return templates.TemplateResponse(request, "admin_otp.html", {
            "request": request, 
            "message": f"OTP successfully sent to your email ({email})"
        })
        
    except Exception as e:
        return templates.TemplateResponse(request, "admin_login.html", {"request": request, "error": f"Failed to send email: {str(e)}"})





@router.post("/admin/verify-otp")
async def verify_admin_otp(request: Request, otp_input: str = Form(...)):
    # 1. MongoDB se directly check karein ki kya is OTP ka koi valid record hai
    # (Agar 5 min ho gaye honge to MongoDB ise khud hi delete kar chuka hoga)
    otp_record = otps_collection.find_one({"otp": otp_input})
    
    if not otp_record:
        return templates.TemplateResponse(request, "admin_otp.html", {
            "request": request, 
            "error": "OTP has expired or is invalid! Please request a new one."
        })
        
    # 2. Agar OTP sahi mil jata hai, toh authentication state active karein
    # Note: Dashboard session ke liye abhi bhi ek dynamic temporary flat session update kar sakte hain
    admin_session_state["is_authenticated"] = True
    
    # 3. Use kiya hua OTP database se turant delete kar dein takki dobara use na ho sake
    otps_collection.delete_one({"_id": otp_record["_id"]})
    
    return responses.RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)



@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    # Strict Verification check
    if not admin_session_state.get("is_authenticated"):
        return responses.RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

    total_books = books_collection.count_documents({})
    total_categories = categories_collection.count_documents({})

    total_members = users_collection.count_documents({})
    issued_books = issued_books_collection.count_documents({"status": "Issued"})

    now = datetime.now(timezone.utc)
    overdue_books = issued_books_collection.count_documents(
    {
        "status": "Issued",
        "due_date": {"$lt": now}
    }
)



        
    return templates.TemplateResponse(request,"admin_dashboard.html", {"request": request,
            "total_books": total_books,
            "total_categories": total_categories,
            "total_members": total_members,
            "issued_books": issued_books,
            "overdue_books": overdue_books})




@router.get("/logout")
async def admin_logout():
    # 1. Server memory se authentication state ko clear karein
    if "is_authenticated" in admin_session_state:
        del admin_session_state["is_authenticated"]
    
    # 2. Clear all session state
    admin_session_state.clear()
    
    # 3. Direct login page (/admin) par redirect karein
    return responses.RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)