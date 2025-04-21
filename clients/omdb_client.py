from typing import List, Optional
from clients.base import MovieDataSupplier
from schemas.movie import Movie
from config.settings import settings
from httpx import AsyncClient
from fastapi import HTTPException

class OMDBClient(MovieDataSupplier):
    __OMDB_BASE_URL = "https://www.omdbapi.com/"

    async def search(
        self,
        title: Optional[str],
        media_type: Optional[str],
        genre: Optional[str],
        actors: Optional[List[str]]
    ) -> List[Movie]:
        if not title:
            # Throw Exception
            return HTTPException(status_code=404)

        endpoint = f"{self.__OMDB_BASE_URL}?apikey={settings.OMDB_API_KEY}&s={title}"

        if media_type:
            endpoint += (f"&type={media_type}")

        print("endpoint: " + endpoint)

        async with AsyncClient() as client:
            response = await client.get(endpoint)
            print(response.json())
            results = response.json().get("Search", {})

        return list(results)