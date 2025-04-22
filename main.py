from fastapi import FastAPI
from typing import Annotated, List, Optional
from fastapi import Depends, Query
from dependencies import get_movie_service
from services.movie_service import MovieService

app = FastAPI()

@app.get("/movies/search/")
async def search_movies(

    # Dependencies
    service: Annotated[MovieService, Depends(get_movie_service)],
    
    # Search query params
    title: Annotated[Optional[str], Query()] = None,
    media_type: Annotated[str, Query()] = "movie",
    actors: Annotated[Optional[List[str]], Query()] = None,
    genre: Annotated[Optional[str], Query()] = None,
    page: int = 1,
):
    
    return await service.search_movies(title, media_type, actors, genre, page)
