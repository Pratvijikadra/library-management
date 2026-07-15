import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()


mongo_uri = os.getenv("MONGO_URI")


client = MongoClient(
    mongo_uri,
    tlsCAFile=certifi.where()
)

try:
    client.admin.command("ping")
    print("MongoDB Connected Successfully")
except Exception as e:
    print("Connection Error:", e)

db = client["library_management"] # database
users_collection = db["users"] #collection
books_collection = db["books"]
categories_collection = db["categories"]
languages_collection = db["languages"]
otps_collection = db["otp"]
issued_books_collection = db["issued_books"]

wishlist_collection = db["wishlist"]

reservations_collection = db["reservations"]

notifications_collection = db["notifications"]

reviews_collection = db["reviews"]
