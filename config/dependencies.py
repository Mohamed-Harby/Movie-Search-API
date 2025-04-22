

from services.movie_service import MovieService


def get_movie_service():
    return MovieService()


# def get_redis_client():
#     return redis.Redis(host=config("REDIS_HOST", "localhost"), port=6379, db=0)