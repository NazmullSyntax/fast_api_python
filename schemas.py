from typing import Optional
from pydantic import BaseModel, Field

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, example="The Pragmatic Programmer")
    author: str = Field(..., min_length=1, max_length=50, example="Andrew Hunt")
    published_year: int = Field(..., ge=1800, le=2026, example=1999)
    genre: Optional[str] = Field(None, example="Software Engineering")

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = Field(None, min_length=1, max_length=50)
    published_year: Optional[int] = Field(None, ge=1800, le=2026)
    genre: Optional[str] = None

class BookResponse(BookBase):
    id: int

    class Config:
        from_attributes = True