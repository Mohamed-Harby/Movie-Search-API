from typing import List, Optional
from httpx import AsyncClient
from clients.base import MovieDataSupplier
from config.settings import settings
from schemas.movie import Movie
from fastapi import HTTPException

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
                    headers=self.headers
                )
                results = resp.json().get("results")
                if results:
                    ids.append(str(results[0]["id"]))
        return ids


    async def __get_genre_id(self, name: str, media_type: str) -> Optional[str]:
        endpoint = f"{self.__TMDB_BASE_URL}/genre/{media_type}/list"
        async with AsyncClient() as client:
            resp = await client.get(endpoint, headers=self.headers)
            genres = resp.json().get("genres", [])
            for genre in genres:
                if genre["name"].lower() == name.lower():
                    return str(genre["id"])
        return None


    async def __search_by_title(self, title: str, media_type: str):
        endpoint = f"{self.__TMDB_BASE_URL}/search/{media_type}?query={title}"

        async with AsyncClient() as client:
            response = await client.get(endpoint, headers=self.headers)
            results = response.json().get("results")
            return results
        
    async def __search_by_actors_and_genre(
            self,
            title: str,
            media_type: str,
            actors: List[str],
            genre: str
    ):
        params = {}
        results = []
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
            response = await client.get(endpoint, params=params, headers=self.headers)
            results = response.json().get("results")

        # Filter title manually
            if title:
                results = [
                    r for r in results
                    if title.lower() in r.get("title").lower() 
                ]
            
        return results

    async def search(
            self,
            title: Optional[str],
            media_type: str,
            actors: Optional[List[str]],
            genre: Optional[str]
        ) -> List[Movie]:
        
        if not title and not (actors or genre):
            raise HTTPException(status_code=400, detail="At least one of title, actors, or genre must be provided!")        
        
        
        
        if actors or genre:
            results = await self.__search_by_actors_and_genre(title, media_type, actors, genre)

        results = await self.__search_by_title(title, media_type)
        
        movies = []
        for r in results:
            movies.append(await self.__convert_to_schema(r))

        return movies
    

    async def __get_genre(self, id: int, media_type: str = "movie"):
        endpoint = f"{self.__TMDB_BASE_URL}/genre/{media_type}/list"
        async with AsyncClient() as client:
            resp = await client.get(endpoint, headers=self.headers)
            genres = resp.json().get("genres", [])
            for genre in genres:
                if genre["id"] == id:
                    return str(genre["name"])
        return None

    async def __convert_to_schema(self, api_movie):
        
        movie_genres = []
        
        for genre in api_movie.get("genre_ids"):
            movie_genres.append(await self.__get_genre(genre))


        return Movie(
            title=api_movie.get("title"),
            year=api_movie.get("release_date").split("-")[0],
            genres=movie_genres,
            poster_url=f"https://image.tmdb.org/t/p/w500{api_movie['poster_path']}" if api_movie.get("poster_path") else None,
            source="tmdb"
        )
    