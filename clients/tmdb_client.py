from typing import List, Optional
from httpx import AsyncClient
from clients.base import MovieDataSupplier
from config.settings import settings
from schemas.movie import Movie


class TMDBClient(MovieDataSupplier):
    __TMDB_BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.TMDB_API_KEY}",
            "accept": "application/json"
        }

    async def __get_person_ids(self, names: List[str]) -> List[str]:
        ids = []
        async with AsyncClient() as client:
            for name in names:
                resp = await client.get(
                    f"{self.__TMDB_BASE_URL}/search/person",
                    params={"query": name},
                    headers=self.HEADERS
                )
                results = resp.json().get("results")
                if results:
                    ids.append(str(results[0]["id"]))
        return ids


    async def __get_genre_id(self, name: str, media_type: str) -> Optional[str]:
        endpoint = f"{self.__TMDB_BASE_URL}/genre/{media_type}/list"
        async with AsyncClient() as client:
            resp = await client.get(endpoint, headers=self.HEADERS)
            genres = resp.json().get("genres", [])
            for genre in genres:
                if genre["name"].lower() == name.lower():
                    return str(genre["id"])
        return None

    async def search(
            self,
            title: Optional[str],
            media_type: str,
            actors: Optional[List[str]],
            genre: Optional[str]) -> List[Movie]:
        params = {}

        if actors:
            cast_ids = await self.__get_person_ids(actors)
            if cast_ids:
                params["with_cast"] = ",".join(cast_ids)

        if genre:
            genre_id = await self.__get_genre_id(genre, media_type)
            if genre_id:
                params["with_genres"] = genre_id

        endpoint = f"{self.__TMDB_BASE_URL}/discover/{media_type}"
        async with AsyncClient() as client:
            resp = await client.get(endpoint, params=params, headers=self.HEADERS)
            results = resp.json().get("results", [])

        # Filter title manually
        if title:
            results = [
                r for r in results
                if title.lower() in r.get("title", r.get("name", "")).lower()
            ]

        movies = []

        for r in results:
            movie = Movie(
            title=r.get("title"),
            year=r.get("release_date").split("-")[0],
            genre=r.get("genre_ids"),
            poster_url=f"https://image.tmdb.org/t/p/w500{r['poster_path']}" if r.get("poster_path") else None,
            source="tmdb"
            )
            movies.append(movie)

        return results