from typing import Annotated, List, Optional
from clients.base import MovieDataSupplier
from clients.omdb_client import OMDBClient
from clients.tmdb_client import TMDBClient
from fastapi import APIRouter, Query, Depends
from services.movie_service import MovieService

router = APIRouter()



def get_movie_service():
    return MovieService()



def get_movie_supplier(supplier: str) -> MovieDataSupplier:
    match supplier:
        case "omdb":
            return OMDBClient()
        case _:
            return TMDBClient()
    


@router.get("/search")
async def search_movies_endpoint(
    title: Annotated[Optional[str], Query()] = None,
    media_type: Annotated[str, Query()] = "movie",
    actors: Annotated[Optional[List[str]], Query()] = None,
    genre: Annotated[Optional[str], Query()] = None,
    supplier: Annotated[Optional[str], Query()] = "tmdb"
):
    
    service: MovieService = MovieService(get_movie_supplier(supplier))
    return await service.search_movies(title, media_type, genre, actors)
