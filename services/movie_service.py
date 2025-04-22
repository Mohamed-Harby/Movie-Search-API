from typing import List, Optional

from fastapi import HTTPException
from suppliers.base import Supplier
from schemas.movie import Movie
from suppliers.omdb_supplier import OMDBSupplier
from suppliers.tmdb_supplier import TMDBSupplier

class MovieService:

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
            return await TMDBSupplier().search(title, media_type, actors, genre, page)
        except HTTPException as exception:
            try:
                return await OMDBSupplier().search(title, media_type, page)
            except HTTPException:
                raise exception


