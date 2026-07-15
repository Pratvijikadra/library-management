from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime
from pydantic.config import ConfigDict
from typing import Annotated

HttpUrl = Annotated[str, HttpUrl]

class Books(BaseModel):
    title: str = Field(..., description="Title of the book")
    isbn: str = Field(..., description="ISBN of the book")
    # author_id: int = Field(..., description="Author ID of the book")
    author_name: str = Field(..., strip_whitespace=True, description="Author name of the book")
    # publisher_id: int = Field(..., description="Publisher ID of the book")
    publisher_name: str = Field(..., strip_whitespace=True, description="Publisher name of the book")
    # category_id: int = Field(..., description="Category ID of the book")
    # category_name: str = Field(..., strip_whitespace=True, description="Category name of the book")
    # language: str = Field(..., strip_whitespace=True, description="Language of the book")
    category_name: str = Field(..., strip_whitespace=True, description="Must match an existing category")
    language: str = Field(..., strip_whitespace=True, description="Must match an existing language")
    edition: str = Field(..., description="Edition of the book")
    published_year: int = Field(..., description="Published year of the book")
    pages: int = Field(..., description="Number of pages in the book")
    shelf_no: str = Field(..., description="Shelf number of the book")
    total_copies: int = Field(..., description="Total copies of the book")
    available_copies: int = Field(..., description="Available copies of the book")
    cover_image: HttpUrl = Field(
        ..., 
        description="Cover image URL of the book (must be a valid HTTP/HTTPS link)"
    )
    description: Optional[str] = Field(default=None, description="Description of the book")
    status: str = Field(..., description="Status of the book")
    created_at: datetime = Field(default_factory=datetime.now, description="Created at time of the book")
    updated_at: datetime = Field(default_factory=datetime.now, description="Updated at time of the book")

    average_rating: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=5.0,
        description="Average rating of the book (0.0 to 5.0)"
    )
    reviews_count: Optional[int] = Field(
        default=0,
        ge=0,
        description="Number of reviews for the book"
    )

    model_config = ConfigDict(extra="ignore")





class CategorySchema(BaseModel):
    name: str = Field(..., strip_whitespace=True, description="Name of the category (e.g., Fiction, Sci-Fi)")

class LanguageSchema(BaseModel):
    name: str = Field(..., strip_whitespace=True, description="Name of the language (e.g., Hindi, English)")


