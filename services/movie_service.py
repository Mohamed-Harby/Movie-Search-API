from typing import List, Optional

from fastapi import HTTPException
from cache import Cache
from suppliers.supplier import Supplier
from schemas.movie import Movie
from suppliers.omdb_supplier import OMDBSupplier
from suppliers.tmdb_supplier import TMDBSupplier


class MovieService:

    def __init__(self, cache: Cache):
        self.cache = cache
        self.omdb_supplier = OMDBSupplier(cache)
        self.tmdb_supplier = TMDBSupplier(cache)

    async def search_movies(
        self,
        title: Optional[str],
        media_type: str,
        actors: Optional[List[str]],
        genre: Optional[str],
        page: int,
    ) -> List[Movie]:

        # Ensure at least one of title, actors, or genre is provided
        if not any([title, actors, genre]):
            raise HTTPException(
                status_code=400,
                detail="Provide at least one of title, actors, or genre.",
            )

        # Ensure not all of title, actors, and genre are provided as no one supplier supports all these filters.
        if all([title, actors, genre]):
            raise HTTPException(
                status_code=400,
                detail="Provide only title or any other filters without title.",
            )

        # Case 1: IF searching by actors or genre or both, only tmdb can handle this
        if actors or genre:
            return await self.tmdb_supplier.search(
                actors=actors, genre=genre, media_type=media_type, page=page
            )

        # Case 2: If only title is provided, try omdb first, then fallback to tmdb
        try:
            return await self.omdb_supplier.search(
                title=title, media_type=media_type, page=page
            )
        except HTTPException:
            # If omdb supplier failed, fallback to tmdb
            return await self.tmdb_supplier.search(
                title=title,
                media_type=media_type,
                page=page,
            )
