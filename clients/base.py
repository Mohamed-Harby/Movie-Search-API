from abc import ABC
from typing import List, Optional
from schemas.movie import Movie


class MovieDataSupplier(ABC):
    async def search(
        self,
        title: Optional[str],
        media_type: str,
        genre: Optional[str],
        actors: Optional[List[str]]
    ) -> List[Movie]:
        pass
