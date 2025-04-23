from typing import List, Optional
from httpx import AsyncClient
from cache import Cache
from suppliers.supplier import Supplier
from config.settings import settings
from schemas.movie import Movie
from fastapi import HTTPException


class TMDBSupplier(Supplier):
    BASE_URL = "https://api.themoviedb.org/3"  # tmdb API base endpoint

    def __init__(self, cache: Cache):
        self.cache = cache  # Injected cache instance
        self.headers = {
            "Authorization": f"Bearer {settings.TMDB_API_KEY}",
            "accept": "application/json",
        }

    async def search(
        self,
        title: Optional[str] = None,
        media_type: str = "movie",
        actors: Optional[List[str]] = None,
        genre: Optional[str] = None,
        page: int = 1,
    ) -> List[Movie]:
        # Ensure that at least one search criterion is provided
        if not title and not (actors or genre):
            raise HTTPException(
                status_code=400,
                detail="At least one of title, actors, or genre must be provided!",
            )

        # Choose appropriate search strategy based on input
        if actors or genre:
            results = await self.search_by_actors_and_genre(
                media_type, actors, genre, page
            )
        else:
            results = await self.search_by_title(title, media_type, page)

        return results

    async def get_person_ids(self, names: List[str]) -> List[str]:
        # Get tmdb person IDs for a list of actor names
        ids = []
        for name in names:
            person_id = await self.get_person_id(name)
            if person_id:
                ids.append(person_id)
        ids.sort()
        return ids

    async def get_person_id(self, name: str) -> str:
        # Check cache first
        cache_key = f"tmdb:person:name:{name.lower()}"
        cached_value = self.cache.get(cache_key)
        if cached_value:
            return cached_value

        # Query tmdb API for person ID
        async with AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/search/person",
                params={"query": name},
                headers=self.headers,
            )
        results = resp.json().get("results")
        if results:
            person_id = str(results[0]["id"])
            self.cache.set(cache_key, person_id, 86400)
            return person_id
        return None

    async def get_genre_id(self, name: str, media_type: str) -> Optional[str]:
        # Get genre ID based on genre name and media type
        genres = await self.get_type_genres(media_type)
        for genre in genres:
            if genre["name"].lower() == name.lower():
                return genre["id"]

    async def get_type_genres(self, media_type: str) -> list:
        # Retrieve genres for a given media type, using cache if available
        cache_key = f"tmdb:type:{media_type.lower()}"
        cached_value = self.cache.get(cache_key)
        if cached_value:
            return cached_value

        async with AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/genre/{media_type}/list", headers=self.headers
            )
            genres = resp.json().get("genres", [])

        genres = sorted(genres, key=lambda genre: genre["name"])
        self.cache.set(cache_key, genres, 86400)
        return genres

    async def search_by_title(self, title: str, media_type: str, page: int):
        # Check if results are cached
        cache_key = f"tmdb:search:title:{title}:type:{media_type}:page:{page}"
        cached_value = self.cache.get(cache_key)
        if cached_value:
            return [
                Movie(**item) for item in cached_value
            ]  # Deserialize from json to Movie

        # Query tmdb API by title
        async with AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/search/{media_type}?query={title}&page={page}",
                headers=self.headers,
            )
            results = response.json().get("results")

        # Convert raw data to Movie schema
        results = [await self.convert_to_schema(item) for item in results]

        # Cache the results
        self.cache.set(cache_key, [movie.model_dump() for movie in results], 86400)

        return results

    async def search_by_actors_and_genre(
        self, media_type: str, actors: List[str], genre: str, page: int
    ):
        params = {}
        results = []

        # Normalize media type for tmdb (movie or tv)
        media_type = "tv" if media_type in ("series", "tv") else "movie"

        # Add actor filter to query
        if actors:
            cast_ids = await self.get_person_ids(actors)
            if cast_ids:
                params["with_cast"] = ",".join(cast_ids)

        # Add genre filter to query
        if genre:
            genre_id = await self.get_genre_id(genre, media_type)
            if genre_id:
                params["with_genres"] = genre_id

        params["page"] = page

        # Generate cache key for this combination of filters
        cache_key = f"tmdb:search:genre:{genre_id}:actors:{cast_ids}:type:{media_type}"
        cached_value = self.cache.get(cache_key)

        if cached_value:
            # Return cached results if available
            results = [
                Movie(**item) for item in cached_value
            ]  # Deserialize from json to Movie

        else:
            # Query tmdb API for filtered discovery results
            async with AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/discover/{media_type}",
                    params=params,
                    headers=self.headers,
                )
                results = response.json().get("results")

            results = [await self.convert_to_schema(item) for item in results]
            self.cache.set(cache_key, [movie.model_dump() for movie in results], 86400)

        return results

    async def get_genre(self, id: int, media_type: str = "movie") -> Optional[str]:
        # Retrieve genre name from ID
        type_genres = await self.get_type_genres(media_type)
        for type_genre in type_genres:
            if type_genre["id"] == id:
                return type_genre["name"]
        return None

    async def convert_to_schema(self, api_movie):
        # Convert raw tmdb movie data into the Movie schema format
        movie_genres = []

        # Fetch genre names for genre IDs
        for genre in api_movie.get("genre_ids"):
            movie_genres.append(await self.get_genre(genre))

        return Movie(
            movie_id=str(api_movie.get("id")),
            title=api_movie.get("title"),
            year=api_movie.get("release_date").split("-")[0],
            genres=movie_genres,
            poster_url=(
                f"https://image.tmdb.org/t/p/w500{api_movie['poster_path']}"
                if api_movie.get("poster_path")
                else None
            ),
            supplier="tmdb",  # Indicate data source
        )
