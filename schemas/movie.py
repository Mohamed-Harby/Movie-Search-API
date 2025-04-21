from pydantic import BaseModel
from typing import Optional, List

class Movie(BaseModel):
    title: str
    year: Optional[str]
    genre: Optional[List[str]]
    poster_url: Optional[str]
    source: str
