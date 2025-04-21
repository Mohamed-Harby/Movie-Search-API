from typing import List, Optional
from clients.base import MovieDataSupplier
from schemas.movie import Movie
from config.settings import settings
from httpx import AsyncClient
from fastapi import HTTPException


class OMDBClient(MovieDataSupplier):
    BASE_URL = "https://www.omdbapi.com/"

    async def search(
        self,
        title: Optional[str],
        media_type: Optional[str],
        genre: Optional[str],  # not used by OMDB API
        actors: Optional[List[str]]  # not used by OMDB API
    ) -> List[Movie]:
        
        if not title:
            raise HTTPException(status_code=400, detail="The title is a required field!")

        params = {
            "apikey": settings.OMDB_API_KEY,
            "s": title
        }

        if media_type:
            params["type"] = media_type

        async with AsyncClient() as client:
            response = await client.get(self.BASE_URL, params=params)
            data = response.json()

        results = data.get("Search", [])
        return [self._convert_to_schema(item) for item in results]

    def _convert_to_schema(self, api_movie) -> Movie:
        return Movie(
            title=api_movie.get("Title"),
            year=api_movie.get("Year"),
            genres=[],  # OMDB doesn't provide genre here
            poster_url=api_movie.get("Poster"),
            source="omdb"
        )
