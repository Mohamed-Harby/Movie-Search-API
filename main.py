from fastapi import FastAPI
from api.movies import router as movie_router

app = FastAPI()
app.include_router(movie_router, prefix="/movies", tags=["Movies"])
