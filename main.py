from fastapi import FastAPI, HTTPException, status
from typing import List
from schemas import BookCreate, BookUpdate, BookResponse

app = FastAPI(
    title="Book Management API",
    description="A simple FastAPI example project featuring CRUD operations.",
    version="1.0.0"
)

# In-memory database simulation
books_db = [
    {
        "id": 1,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "published_year": 2008,
        "genre": "Software Development"
    }
]

# Helper function to find a book by ID
def find_book(book_id: int):
    for book in books_db:
        if book["id"] == book_id:
            return book
    return None


@app.get("/", tags=["Health"])
def root():
    return {"message": "Welcome to the FastAPI Book API!"}


@app.get("/api/books", response_model=List[BookResponse], tags=["Books"])
def get_all_books():
    """Retrieve all books."""
    return books_db


@app.get("/api/books/{book_id}", response_model=BookResponse, tags=["Books"])
def get_book(book_id: int):
    """Retrieve a single book by ID."""
    book = find_book(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    return book


@app.post("/api/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED, tags=["Books"])
def create_book(book_data: BookCreate):
    """Create a new book record."""
    new_id = max([b["id"] for b in books_db], default=0) + 1
    new_book = {"id": new_id, **book_data.model_dump()}
    books_db.append(new_book)
    return new_book


@app.put("/api/books/{book_id}", response_model=BookResponse, tags=["Books"])
def update_book(book_id: int, book_data: BookUpdate):
    """Update an existing book record partially or fully."""
    book = find_book(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    update_dict = book_data.model_dump(exclude_unset=True)
    book.update(update_dict)
    return book


@app.delete("/api/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
def delete_book(book_id: int):
    """Delete a book record by ID."""
    book = find_book(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    books_db.remove(book)
    return None