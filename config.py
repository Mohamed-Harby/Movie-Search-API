from dotenv import load_dotenv
import os

load_dotenv()  # load .env file

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
