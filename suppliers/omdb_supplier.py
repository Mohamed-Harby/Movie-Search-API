from typing import List, Optional
from suppliers.base import Supplier
from schemas.movie import Movie
from config.settings import settings
from httpx import AsyncClient
from fastapi import HTTPException


class OMDBSupplier(Supplier):
    BASE_URL = "https://www.omdbapi.com/"

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

        async with AsyncClient() as client:
            response = await client.get(self.BASE_URL, params=params)
            data = response.json()

        results = data.get("Search", [])
        return [self.__convert_to_schema(item) for item in results]

    def __convert_to_schema(self, api_movie) -> Movie:
        return Movie(
            movie_id = api_movie.get("imdbID"),
            title=api_movie.get("Title"),
            year=api_movie.get("Year"),
            genres=[],  # OMDB doesn't provide genre here
            poster_url=api_movie.get("Poster"),
            source="omdb"
        )
