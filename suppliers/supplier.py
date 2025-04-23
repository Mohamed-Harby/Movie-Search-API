from abc import ABC, abstractmethod
from typing import List, Optional
from schemas.movie import Movie


class Supplier(ABC):
    @abstractmethod
    async def search(
        self,
        title: Optional[str] = None,
        media_type: str = "movie",
        genre: Optional[str] = None,
        actors: Optional[List[str]] = None,
        page: int = 1,
    ) -> List[Movie]:
        pass
