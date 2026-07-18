import os
import sys
# Add parent directory to path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import books_collection

def migrate_status():
    books = books_collection.find()
    updated_count = 0
    for book in books:
        available_copies = book.get("available_copies", 0)
        new_status = "Available" if available_copies > 0 else "Unavailable"
        if book.get("status") != new_status:
            books_collection.update_one(
                {"_id": book["_id"]},
                {"$set": {"status": new_status}}
            )
            updated_count += 1
            print(f"Updated '{book.get('title')}' to {new_status}")
    print(f"Migration complete. Updated {updated_count} books.")

if __name__ == "__main__":
    migrate_status()
