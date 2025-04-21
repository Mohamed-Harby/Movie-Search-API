from typing import List, Optional
from clients.base import MovieDataSupplier
from schemas.movie import Movie

class MovieService:
    def __init__(self, provider: MovieDataSupplier):
        self.provider = provider

    async def search_movies(
        self,
        title: Optional[str],
        media_type: str,
        actors: Optional[List[str]],
        genre: Optional[str]
    ) -> List[Movie]:
        return await self.provider.search(title, media_type, genre, actors)


