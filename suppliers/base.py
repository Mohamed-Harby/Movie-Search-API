from abc import ABC, abstractmethod
from typing import List, Optional
from schemas.movie import Movie, SearchResponse


class Supplier(ABC):
    @abstractmethod
    async def search(
        self,
        title: Optional[str],
        media_type: str,
        genre: Optional[str],
        actors: Optional[List[str]],
        page: int
    ) -> List[Movie]:
        pass
