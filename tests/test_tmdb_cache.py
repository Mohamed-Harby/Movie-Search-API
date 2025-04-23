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


# Test that search results by title are cached correctly
@pytest.mark.asyncio
async def test_result_is_cached_search_by_title(cache, supplier):
    # Perform a search by title
    result: List[Movie] = await supplier.search(
        title="last", media_type="movie", page=1
    )
    # Retrieve the cached result using the expected cache key
    cached_result = cache.get(f"tmdb:search:title:last:type:movie:page:1", Movie)
    assert result == cached_result


# Test that search results by actors and genre are cached correctly
@pytest.mark.asyncio
async def test_result_is_cached_search_by_actors_and_genre(cache, supplier):
    # Perform a search by actors and genre
    result: List[Movie] = await supplier.search(
        actors=["Tom Cruise"],
        genre="Action",
        page=1,
    )
    # Retrieve actor and genre IDs to construct the cache key
    actor_id = await supplier.get_person_id("Tom Cruise")
    genre_id = await supplier.get_genre_id("Action", "movie")

    # Retrieve the cached result using the expected cache key
    cached_result = cache.get(
        f"tmdb:search:genre:{genre_id}:actors:{[actor_id]}:type:movie", Movie
    )
    assert result == cached_result


# Test that person IDs are cached correctly
@pytest.mark.asyncio
async def test_person_id_cached(cache, supplier):
    # Retrieve the person ID for a given name
    person_id = await supplier.get_person_id("Will Smith")

    # Retrieve the cached result using the expected cache key
    cached_result = cache.get(f"tmdb:person:name:will smith")

    assert person_id == cached_result


# Test that type genres (e.g., movie genres) are cached correctly
@pytest.mark.asyncio
async def test_type_genres_cached(cache, supplier):
    # Retrieve the genres for a specific media type
    person_id = await supplier.get_type_genres("movie")

    # Retrieve the cached result using the expected cache key
    cached_result = cache.get(f"tmdb:type:movie")

    assert person_id == cached_result
