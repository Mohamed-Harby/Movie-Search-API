from typing import List, Optional
from cache import Cache
from suppliers.supplier import Supplier
from schemas.movie import Movie
from config.settings import settings
from httpx import AsyncClient
from fastapi import HTTPException


class OMDBSupplier(Supplier):
    BASE_URL = "https://www.omdbapi.com/"  # omdb API base endpoint

    def __init__(self, cache: Cache):
        self.cache = cache  # Injected cache instance for storing/retrieving responses

    async def search(
        self,
        title: Optional[str],
        media_type: str,
        genre: Optional[str] = None,
        actors: Optional[List[str]] = None,
        page: int = 1,
    ) -> List[Movie]:

        # Title is mandatory for omdb search
        if not title:
            raise HTTPException(
                status_code=400, detail="The title is a required field!"
            )

        # Prepare request parameters for the API call
        params = {"apikey": settings.OMDB_API_KEY, "s": title, "page": page}

        # omdb API accepts type as "movie" or "series"
        if media_type:
            params["type"] = (
                "series" if media_type == "series" else "movie"
            )  # Defaulting to "movie"

        # Generate a unique cache key for this query
        cache_key = f"omdb:search:title:{title}:type:{media_type}:page:{page}"

        # Check if the result is already in cache
        cached_value = self.cache.get(cache_key)
        if cached_value:
            cached_value

        # Make a request to omdb API
        try:
            async with AsyncClient() as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

                if not data.get("results"):
                    raise HTTPException(
                        status_code=404, detail="No tmdb results found."
                    )
        except Exception as exception:
            raise HTTPException(
                status_code=500, detail=f"Unexpected error from tmdb: {str(exception)}"
            )

        # Extract results and convert them into Movie objects
        results = data.get("Search", [])
        results = [self.convert_to_schema(item) for item in results]

        # Cache the results for 24 hours (86400 seconds)
        self.cache.set(cache_key, [movie.model_dump() for movie in results], 86400)

        return results

    def convert_to_schema(self, api_movie) -> Movie:
        # Transform omdb API response format into internal Movie schema
        return Movie(
            movie_id=api_movie.get("imdbID"),
            title=api_movie.get("Title"),
            year=api_movie.get("Year"),
            genres=[],  # omdb search endpoint doesn't return genres
            poster_url=api_movie.get("Poster"),
            supplier="omdb",  # Identify the data source
        )
