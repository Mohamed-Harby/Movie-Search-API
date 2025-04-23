from typing import List, Optional
from cache import Cache
from suppliers.base import Supplier
from schemas.movie import Movie
from config.settings import settings
from httpx import AsyncClient
from fastapi import HTTPException


class OMDBSupplier(Supplier):
    BASE_URL = "https://www.omdbapi.com/"

    def __init__(self, cache: Cache):
        self.cache = cache

    async def search(
        self,
        title: Optional[str],
        media_type: Optional[str],
        page: int
    ) -> List[Movie]:
        
        if not title:
            raise HTTPException(status_code=400, detail="The title is a required field!")

        params = {
            "apikey": settings.OMDB_API_KEY,
            "s": title,
            "page": page
        }

        if media_type:
            params["type"] = "series" if media_type == "series" else "movie"
        

        cache_key = f"omdb:search:title:{title}:page:{page}"
        cached_value = self.cache.get(cache_key)
        if cached_value:
            return cached_value
        
        async with AsyncClient() as client:
            response = await client.get(self.BASE_URL, params=params)
            data = response.json()

        results = data.get("Search", [])
        results = [self.__convert_to_schema(item) for item in results]

        self.cache.set(cache_key, results, 86400)
        
    def __convert_to_schema(self, api_movie) -> Movie:
        return Movie(
            movie_id = api_movie.get("imdbID"),
            title=api_movie.get("Title"),
            year=api_movie.get("Year"),
            genres=[],  # OMDB doesn't provide genre here
            poster_url=api_movie.get("Poster"),
            source="omdb"
        )
