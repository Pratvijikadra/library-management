# 📚 Library Management System

A modern **Library Management System** built with **FastAPI**, **MongoDB Atlas**, **Jinja2 Templates**, **Bootstrap 5**, and **JWT Authentication**.
The system provides separate interfaces for **Users** and **Admin**, enabling efficient management of books, issued, reservations, and user accounts.

## 🎬 Project Demo Video
User Side : https://drive.google.com/file/d/1BWcKy1qBakXcRy9WG2126ZxjRfZml9cl/view?usp=sharing
Admin Side : https://drive.google.com/file/d/1FAMGJPfIbxREc9F8acr3WQ0K3dRhv1I2/view?usp=sharing

## 🚀 Features

### 👤 User Features

- User Registration & Login
- Secure JWT Authentication
- Browse Library Books
- Live Book Search Suggestions
- Filter Books by Category,Language
- Sort Books
- View Book Details
- Issue Books
- Return Books
- Reserve Books
- Reading History
- My Library
- My Account
- Update Profile
- Change Password
- Overdue Fine Calculation (₹5 per day)
- Dynamic Dashboard
- Toast Notifications
- Pagination System

---

### 👨‍💼 Admin Features

- Secure Admin Login
- Email OTP Verification
- JWT Based Admin Session
- Dashboard Analytics
- Manage Books,Categories,Languages
- Issue/return Book Monitoring
- Member management

---

## 🛠 Tech Stack

### Backend

- FastAPI
- Python
- PyMongo
- MongoDB Atlas
- JWT Authentication
- Bcrypt Password Hashing
- smtp Mail

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Jinja2 Templates
- Font Awesome

### Database

MongoDB Atlas

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/Pratvijikadra/library-management.git
```

```
cd library-management-system
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```
---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Create .env File

```env
MONGO_URI=YOUR_MONGODB_CONNECTION_STRING

SECRET_KEY=YOUR_SECRET_KEY

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_DAYS=Days

ADMIN_EMAIL=your_admin_email@gmail.com

ADMIN_PASSWORD=your_admin_password

MAIL_USERNAME=your_email@gmail.com

MAIL_PASSWORD=your_app_password

MAIL_FROM=your_email@gmail.com

MAIL_PORT=587

MAIL_SERVER=smtp.gmail.com

```

---

## Run Application

```bash
uvicorn main:app --reload
```

Open

```
http://127.0.0.1:8000
```

# 🔐 Authentication

### User

- JWT Authentication
- Secure Password Hashing
- Cookie Based Session

### Admin

- Email + Password Login
- OTP Verification
- OTP Valid for 5 minutes only
- JWT Authentication

---

# 👨‍💻 Author

**Pratvi Jikadra**

Python Full Stack Developer

GitHub : https://github.com/Pratvijikadra

LinkedIn: https://linkedin.com/in/yourprofile

---

It motivates me to build more awesome projects.
