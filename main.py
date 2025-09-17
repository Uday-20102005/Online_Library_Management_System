import os
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
import sys

# Load .env variables
load_dotenv()

# Supabase credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def add_member():
    name = input("Member name: ")
    email = input("Member email: ")

    # Check if the email already exists
    existing = supabase.table("members").select("*").eq("email", email).execute()

    if existing.data:
        print(f"Error: Member with email '{email}' already exists.")
        return

    resp = supabase.table("members").insert({"name": name, "email": email}).execute()
    print("Added Member:", resp.data)

def add_book():
    title = input("Book title: ")
    author = input("Book author: ")
    category = input("Book category: ")
    stock = int(input("Stock quantity: "))
    resp = supabase.table("books").insert({
        "title": title,
        "author": author,
        "category": category,
        "stock": stock
    }).execute()
    print("Added Book:", resp.data)


def list_books():
    resp = supabase.table("books").select("*").execute()
    print("\n--- Book List ---")
    for book in resp.data:
        print(book)


def search_books():
    keyword = input("Search keyword: ")
    resp = supabase.table("books").select("*").or_(
        f"title.ilike.%{keyword}%,author.ilike.%{keyword}%,category.ilike.%{keyword}%"
    ).execute()
    print("\n--- Search Results ---")
    for book in resp.data:
        print(book)


def show_member():
    member_id = int(input("Member ID: "))
    member_resp = supabase.table("members").select("*").eq("member_id", member_id).execute()
    if not member_resp.data:
        print("Member not found.")
        return

    member = member_resp.data[0]
    print("\nMember Details:", member)

    borrow_resp = supabase.table("borrow_records").select("book_id, return_date, books(title)").eq("member_id", member_id).execute()
    print("\nBorrow Records:")
    for br in borrow_resp.data:
        status = "Returned" if br["return_date"] else "Not returned"
        print(f"Book ID: {br['book_id']}, Title: {br['books']['title']}, Status: {status}")


def update_book_stock():
    book_id = int(input("Book ID: "))
    stock = int(input("New stock quantity: "))
    resp = supabase.table("books").update({"stock": stock}).eq("book_id", book_id).execute()
    print("Stock Updated:", resp.data)


def update_member_email():
    member_id = int(input("Member ID: "))
    email = input("New email: ")
    resp = supabase.table("members").update({"email": email}).eq("member_id", member_id).execute()
    print("Email Updated:", resp.data)


def delete_member():
    member_id = int(input("Member ID to delete: "))
    supabase.table("members").delete().eq("member_id", member_id).execute()
    print(f"Member {member_id} deleted.")


def delete_book():
    book_id = int(input("Book ID to delete: "))
    supabase.table("books").delete().eq("book_id", book_id).execute()
    print(f"Book {book_id} deleted.")


def borrow_book():
    member_id = int(input("Member ID: "))
    book_id = int(input("Book ID: "))

    book_resp = supabase.table("books").select("stock").eq("book_id", book_id).execute()
    if not book_resp.data:
        print("Book not found.")
        return

    book = book_resp.data[0]
    if book["stock"] < 1:
        print("Book not available.")
        return

    supabase.table("books").update({"stock": book["stock"] - 1}).eq("book_id", book_id).execute()
    supabase.table("borrow_records").insert({
        "member_id": member_id,
        "book_id": book_id
    }).execute()

    print("Book borrowed successfully.")


def return_book():
    member_id = int(input("Member ID: "))
    book_id = int(input("Book ID: "))

    borrow_resp = supabase.table("borrow_records").select("*").eq("member_id", member_id).eq("book_id", book_id).is_("return_date", None).execute()

    if not borrow_resp.data:
        print("No active borrow record found.")
        return

    borrow = borrow_resp.data[0]

    supabase.table("borrow_records").update({"return_date": datetime.utcnow().isoformat()}).eq("record_id", borrow["record_id"]).execute()

    book_resp = supabase.table("books").select("stock").eq("book_id", book_id).execute()
    book = book_resp.data[0]

    supabase.table("books").update({"stock": book["stock"] + 1}).eq("book_id", book_id).execute()

    print("Book returned successfully.")


def main():
    while True:
        print("""
--- Library Management System ---
1. Add Member
2. Add Book
3. List Books
4. Search Books
5. Show Member Details
6. Update Book Stock
7. Update Member Email
8. Delete Member
9. Delete Book
10. Borrow Book
11. Return Book
12. Exit
""")
        choice = input("Choose option: ")

        options = {
            "1": add_member,
            "2": add_book,
            "3": list_books,
            "4": search_books,
            "5": show_member,
            "6": update_book_stock,
            "7": update_member_email,
            "8": delete_member,
            "9": delete_book,
            "10": borrow_book,
            "11": return_book,
            "12": lambda: sys.exit(0)
        }

        action = options.get(choice)
        if action:
            action()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
