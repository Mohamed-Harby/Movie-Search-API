# Movies Search API


## Project Overview
The Movie Search API is a RESTful service built with FastAPI that allows users to search for movies by various criteria such as title, actors, type (movie or series), and genre. The service integrates with external movie data providers to fetch and return structured JSON responses.


## Tech Stack
- **Framework**: FastAPI
- **Data Validation/Serialization**: Pydantic
- **External APIs**: OMDB API, TMDB API
- **Cache**: Redis
- **Testing**: Pytest

## Setup and run instructions
### Prerequisites

  

1. Python 3.8 or higher installed on your system.
2. API keys for:
    - [OMDB API](https://www.omdbapi.com/apikey.aspx)
    - [TMDB API](https://developer.themoviedb.org/reference/intro/getting-started)

### Steps
1. Clone the repository:

```bash
git clone https://github.com/Mohamed-Harby/Movie-Search-API.git

cd Movie-Search-API
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

  
4. Set up environment variables:

Create a `.env` file in the project root with the following content:

```
OMDB_API_KEY=<your-omdb-api-key>
TMDB_API_KEY=<your-tmdb-api-key>
```

  

5. Run the application:
```bash
uvicorn main:app --reload
```

6. Access the API documentation at `http://127.0.0.1:8000/docs`.


## API reference:
### Endpoint: Search Movies
**URL**: `/movies/search/`
**Method**: `GET`
**Description**: Search for movies based on various criteria such as title, media type, actors, and genre.

---

**Response Body**:
A list of movies matching the search criteria. Each movie is represented as a JSON object with the following fields:

| Field       | Type           | Description                                                                 |
|-------------|----------------|-----------------------------------------------------------------------------|
| `movie_id`  | `string`       | The unique identifier for the movie.                                       |
| `title`     | `string`       | The title of the movie.                                                    |
| `year`      | `string`       | The release year of the movie.                                             |
| `genres`    | `List[string]` | A list of genres associated with the movie.                                |
| `poster_url`| `string`       | The URL of the movie's poster image.                                       |
| `supplier`  | `string`       | The data source for the movie information (e.g., `"omdb"` or `"tmdb"`).   |

---
**Error Responses**
| Status Code | Description                                                                       |
|-------------|-----------------------------------------------------------------------------------|
| `400`       | Bad Request. Missing required parameters or invalid combination of filters.      |
| `404`       | No results found for the given search criteria.                                  |
| `422`       | Validation error for query parameters (e.g., invalid data type).                 |
| `500`       | Internal server error.                                                           |

---
**Example Requests**
1. **Search by Title**

```bash
GET /movies/search/?title=Inception
```
**Response**
```json
[
    {
        "movie_id": "tt1375666",
        "title": "Inception",
        "year": "2010",
        "genres": ["Action", "Sci-Fi"],
        "poster_url": "https://example.com/inception.jpg",
        "supplier": "omdb"
    }
]
```
--- 
2. **Search by Actors and Genre**

```bash
GET GET /movies/search/?actors=Leonardo%20DiCaprio&genre=Drama
```
**Response**
```json
[
    {
        "movie_id": "tt0407887",
        "title": "The Departed",
        "year": "2006",
        "genres": ["Crime", "Drama"],
        "poster_url": "https://example.com/thedeparted.jpg",
        "supplier": "tmdb"
    }
]
```

--- 
3. **nvalid Request (Missing Parameters)**

```bash
GET /movies/search/
```
**Response**
```json
{
    "detail": "Provide at least one of title, actors, or genre."
}
```

Notes
- The API integrates with external movie data providers (OMDB and TMDB) to fetch movie information.
- Results are cached using Redis to improve performance and reduce external API calls.
- The media_type parameter defaults to "movie" but can also accept "series" for TV shows.

## Design decisions
- Delivered a consistent user experience, the API uses a backend-driven approach to select between `TMDB` and `OMDB` based on query paramaters. This abstracts supplier differences from end users, ensuring a unified API contract.



- Created Supplier abstract base class `Supplier` that defines a common interface, with concrete implementations (`TMDBSupplier`, `OMDBSupplier`) handling API calls and data normalization into the Movie Pydantic model. This isolates supplier differences and maintains a consistent response format. This supports extensibility, and adheres to the Single Responsibility Principle.  Adding a new supplier requires only a new supplier class and registration in `MovieService`.

- Implemented unified API Contract with Pydantic Model `Movie`. It also supports future suppliers without breaking existing clients.

- Cached third party API respones to reduce external requests, and improve response times. Search queries in addition to other necessary queries responses are cached for fast retrival.

- Implemeted `Cache` class that has genric code for data serialization and deserialization for the pydantic models.

- Implemented comprehensive error handling using `try except` block and implemented fallback to different supplier when exceptions happen.


## Limitations and possible improvements
### Supporting all search criteria
**Limitation**: No single API can support search with full search criteria.

**Possible Improvements**:
- Search with all possible criteria then, manually filter the response data.
- Integrate with other suppliers that supports all needed search criteria.

### Make response more rich

**Limitation**: The date of search responses coming from third party APIs are not rich.

**Possible Improvement**: Other calls can be performed to get more data about each movie. This will require making maing external API requests but we can use proper caching mechanism.

