from typing import List, Optional

from fastapi import HTTPException
from cache import Cache
from suppliers.base import Supplier
from schemas.movie import Movie
from suppliers.omdb_supplier import OMDBSupplier
from suppliers.tmdb_supplier import TMDBSupplier

class MovieService:

    def __init__(self, cache: Cache):
        self.cache = cache

    async def search_movies(
        self,
        title: Optional[str],
        media_type: str,
        actors: Optional[List[str]],
        genre: Optional[str],
        page: int
    ) -> List[Movie]:
        

        if not any([title, actors, genre]):
            raise HTTPException (status_code=400, detail="Provide at least one of title, actors, or genre.")

        try:
            return await TMDBSupplier(self.cache).search(title=title, media_type=media_type,
                                               actors=actors, genre=genre, page=page)
        except HTTPException as exception:
            try:
                return await OMDBSupplier(self.cache).search(title=title, media_type=media_type, page=page)
            except HTTPException:
                raise exception


