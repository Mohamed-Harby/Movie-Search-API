from pydantic import BaseModel
from typing import Optional, List

class Movie(BaseModel):
    title: str
    year: Optional[str]
    genres: Optional[List[str]]
    poster_url: Optional[str]
    source: str
