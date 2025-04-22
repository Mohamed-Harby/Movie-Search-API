from typing import Annotated

from fastapi import Depends
from cache import Cache
from services.movie_service import MovieService


def get_cache() -> Cache:
    return  Cache()


def get_movie_service(cache: Annotated[Cache, Depends(get_cache)]) -> MovieService:
    return MovieService(cache)
