from typing import Annotated, List, Optional
from config.dependencies import get_movie_service
from suppliers.base import Supplier
from suppliers.omdb_supplier import OMDBSupplier
from suppliers.tmdb_supplier import TMDBSupplier
from fastapi import APIRouter, Depends, Query
from services.movie_service import MovieService

router = APIRouter()




@router.get("/search")
async def search_movies_endpoint(
    title: Annotated[Optional[str], Query()] = None,
    media_type: Annotated[str, Query()] = "movie",
    actors: Annotated[Optional[List[str]], Query()] = None,
    genre: Annotated[Optional[str], Query()] = None,
    page: int = 1,
    service: MovieService = Depends(get_movie_service)
):
    
    
    return await service.search_movies(title=title, media_type=media_type, 
                                       genre=genre, actors=actors, page=page)
