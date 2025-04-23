from typing import List
import pytest
from schemas.movie import Movie
from suppliers.omdb_supplier import OMDBSupplier
from cache import Cache


@pytest.fixture
def cache():
    return Cache()


@pytest.fixture
def supplier(cache):
    return OMDBSupplier(cache)


@pytest.mark.asyncio
async def test_result_is_cached(cache, supplier):
    # Perform a search by title using the OMDB supplier
    result: List[Movie] = await supplier.search(
        title="gang", media_type="movie", page=1
    )
    # Retrieve the cached result using the expected cache key
    cached_result = cache.get(f"omdb:search:title:gang:type:movie:page:1", Movie)
    assert result == cached_result
