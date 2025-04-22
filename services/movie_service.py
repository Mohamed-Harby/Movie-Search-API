from typing import List, Optional
from clients.base import Supplier
from schemas.movie import Movie

class MovieService:
    def __init__(self, movie_data_supplier: Supplier):
        self.movie_data_supplier = movie_data_supplier

    async def search_movies(
        self,
        title: Optional[str],
        media_type: str,
        actors: Optional[List[str]],
        genre: Optional[str]
    ) -> List[Movie]:
        return await self.movie_data_supplier.search(title, media_type, genre, actors)


