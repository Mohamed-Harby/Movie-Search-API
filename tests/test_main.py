import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# Test that a search with valid parameters but no suitable supplier returns a 400 status code
@pytest.mark.asyncio
async def test_search_with_valid_params():
    response = client.get(
        "/movies/search/?title=Inception&media_type=movie&actors=Leonardo&genre=Sci-Fi&page=1"
    )
    print(response.json())
    assert response.status_code == 400


# Test that a search with an invalid page type returns a 422 status code
@pytest.mark.asyncio
async def test_search_with_invalid_page_type():
    response = client.get("/movies/search/?title=Inception&page=abc")
    assert response.status_code == 422


# Test that a search with no parameters returns a 400 status code
@pytest.mark.asyncio
async def test_search_with_no_params():
    response = client.get("/movies/search/")
    assert response.status_code == 400


# Test that a search with only a valid title returns a 200 status code
@pytest.mark.asyncio
async def test_search_movies_valid():
    response = client.get("/movies/search?title=Inception")
    assert response.status_code == 200


# Test that a search with missing required parameters returns a 400 status code
@pytest.mark.asyncio
async def test_search_movies_invalid():
    response = client.get("/movies/search")
    assert response.status_code == 400
