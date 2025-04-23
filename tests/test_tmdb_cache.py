from typing import List
import pytest
from schemas.movie import Movie
from suppliers.tmdb_supplier import TMDBSupplier
from cache import Cache


@pytest.fixture
def cache():
    return Cache()


@pytest.fixture
def supplier(cache):
    return TMDBSupplier(cache)


@pytest.mark.asyncio
async def test_result_is_cached_search_by_title(cache, supplier):
    result: List[Movie] = await supplier.search(
        title="last", media_type="movie", page=1
    )
    cached_result = cache.get(f"tmdb:search:title:last:type:movie:page:1")
    assert result == cached_result


@pytest.mark.asyncio
async def test_result_is_cached_search_by_actors_and_genre(cache, supplier):
    result: List[Movie] = await supplier.search(
        actors=["Tom Cruise"],
        genre="Action",
        page=1,
    )
    actor_id = await supplier.get_person_id("Tom Cruise")
    genre_id = await supplier.get_genre_id("Action", "movie")

    cached_result = cache.get(
        f"tmdb:search:genre:{genre_id}:actors:{[actor_id]}:type:movie"
    )
    assert result == cached_result


@pytest.mark.asyncio
async def test_person_id_cached(cache, supplier):
    person_id = await supplier.get_person_id("Will Smith")

    cached_result = cache.get(f"tmdb:person:name:will smith")

    print(cached_result)
    assert person_id == cached_result


@pytest.mark.asyncio
async def test_type_genres_cached(cache, supplier):
    person_id = await supplier.get_type_genres("movie")

    cached_result = cache.get(f"tmdb:type:movie")

    print(cached_result)
    assert person_id == cached_result
