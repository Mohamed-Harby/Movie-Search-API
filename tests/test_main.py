import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


@pytest.mark.asyncio
async def test_search_with_valid_params():
    response = client.get(
        "/movies/search/?title=Inception&media_type=movie&actors=Leonardo&genre=Sci-Fi&page=1"
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_with_invalid_page_type():
    response = client.get("/movies/search/?title=Inception&page=abc")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_with_no_params():
    response = client.get("/movies/search/")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_search_movies_valid():
    response = client.get("/movies/search?title=Inception")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_movies_invalid():
    response = client.get("/movies/search")
    assert response.status_code == 400
