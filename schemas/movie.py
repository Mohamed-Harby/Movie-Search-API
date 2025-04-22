from pydantic import BaseModel
from typing import Optional, List

class Movie(BaseModel):
    movie_id: str
    title: str
    year: Optional[str]
    genres: List[str]
    actors: List[str]
    media_type: Optional[str]
    poster_url: Optional[str]
    supplier: str


class SearchResponse(BaseModel):
    results: List[Movie]
    total_results: int
    total_pages: int
    page: int
