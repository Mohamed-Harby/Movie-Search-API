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

        # IF searching by actors or genre or both, only tmdb can handle this
        if actors or genre:
            try:
                return await TMDBSupplier(self.cache).search(
                    actors=actors, genre=genre, media_type=media_type, page=page
                )
            except HTTPException as exception:
                raise exception

        # If only title is provided, try OMDB first
        try:
            return await OMDBSupplier(self.cache).search(
                title=title, media_type=media_type, page=page
            )
        except HTTPException as exception:
            try:
                # If omdb supplier failed, fallback to tmdb
                return await TMDBSupplier(self.cache).search(
                    title=title,
                    media_type=media_type,
                    page=page,
                )
            except HTTPException:  # Raise exception if both suppliers failed
                return exception
