

https://drive.google.com/file/d/1BWcKy1qBakXcRy9WG2126ZxjRfZml9cl/view?usp=sharing


# 📚 Library Management System

A modern **Library Management System** built with **FastAPI**, **MongoDB Atlas**, **Jinja2 Templates**, **Bootstrap 5**, and **JWT Authentication**.
The system provides separate interfaces for **Users** and **Admin**, enabling efficient management of books, issued, reservations, and user accounts.

---

## 🚀 Features

### 👤 User Features

- User Registration & Login
- Secure JWT Authentication
- Browse Library Books
- Live Book Search Suggestions
- Filter Books by Category
- Filter Books by Language
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

---

### 👨‍💼 Admin Features

- Secure Admin Login
- Email OTP Verification
- JWT Based Admin Session
- Dashboard Analytics
- Manage Books
- Manage Categories
- Manage Languages
- Issue Book Monitoring
- Overdue Books Monitoring
- Member Statistics

---

## 🛠 Tech Stack

### Backend

- FastAPI
- Python
- PyMongo
- MongoDB Atlas
- JWT Authentication
- Bcrypt Password Hashing
- FastAPI Mail

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Jinja2 Templates
- Font Awesome

### Database

MongoDB Atlas

---

# 📂 Project Structure

```
library_management_system/

│
├── backend/
│   ├── routes/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── books.py
│   │   ├── my_account.py
│   │   └── search.py
│   │
│   ├── database.py
│   └── schemas.py
│
├── frontend/
│   ├── templates/
│   ├── static/
│   ├── css/
│   └── js/
│
├── .env
├── main.py
├── requirements.txt
└── README.md
```

---

# 📦 MongoDB Collections

## users

```
name
email
password
created_at
```

---

## books

```
title
isbn
author_name
publisher_name
category_name
language
edition
published_year
pages
shelf_no
total_copies
available_copies
cover_image
description
status
average_rating
reviews_count
created_at
updated_at
```

---

## categories

```
name
```

---

## languages

```
name
```

---

## issued_books

```
user_id
book_id
issue_date
due_date
return_date
status
fine_amount
fine_paid
```

---

## reservations

```
user_id
book_id
reservation_date
status
```

---

## otp

```
email
otp
verified_email
created_at
```

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/library-management-system.git
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

Linux / Mac

```bash
source venv/bin/activate
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

ACCESS_TOKEN_EXPIRE_DAYS=7

ADMIN_EMAIL=your_admin_email@gmail.com

ADMIN_PASSWORD=your_admin_password

MAIL_USERNAME=your_email@gmail.com

MAIL_PASSWORD=your_app_password

MAIL_FROM=your_email@gmail.com

MAIL_PORT=587

MAIL_SERVER=smtp.gmail.com

MAIL_STARTTLS=True

MAIL_SSL_TLS=False
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

---

# 📸 Screenshots

You can add screenshots here.

- Login Page
- Register Page
- User Dashboard
- Books Page
- Book Details
- My Library
- Reading History
- My Account
- Admin Dashboard

---

# 🔐 Authentication

### User

- JWT Authentication
- Secure Password Hashing
- Cookie Based Session

### Admin

- Email + Password Login
- OTP Verification
- JWT Authentication

---

# 📈 Dashboard Analytics

### User Dashboard

- Total Books
- Borrowed Books
- Reserved Books
- Returned Books
- Reading Progress
- Recent Activity

### Admin Dashboard

- Total Books
- Total Categories
- Total Members
- Issued Books
- Overdue Books

---

# 💰 Fine Policy

```
₹5 Fine Per Day

Fine = Overdue Days × ₹5
```

---

# ✨ Future Improvements

- Book Reviews
- Ratings
- Wishlist
- Email Notifications
- Barcode Scanner
- QR Code Support
- Book Recommendation System
- Dark Mode
- Multi Admin Support
- Profile Photo Upload
- Payment Gateway for Fine
- Reports & Analytics Export
- Mobile Responsive Improvements

---

# 👨‍💻 Author

**Pratvi Jikadra**

Python Full Stack Developer

GitHub: https://github.com/yourusername

LinkedIn: https://linkedin.com/in/yourprofile

---

# ⭐ Support

If you like this project, please give it a ⭐ on GitHub.

It motivates me to build more awesome projects.

---

# 📄 License

This project is developed for learning and portfolio purposes.
