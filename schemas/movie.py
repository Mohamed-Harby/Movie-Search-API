from pydantic import BaseModel
from typing import Optional, List

class Movie(BaseModel):
    movie_id: str
    title: str
    year: Optional[str]
    genres: List[str]
    poster_url: Optional[str]
    supplier: str
