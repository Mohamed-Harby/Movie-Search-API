import redis
import json
from typing import Optional, TypeVar, Type
from pydantic import BaseModel

T = TypeVar("T")

class Cache:
    redis_client = redis.Redis(host="localhost", port=6379, db=0)

    def get(self, key: str, model: Type[T] = None) -> Optional[T]:
        """Retrieve cached data and deserialize to model if provided."""
        data = self.redis_client.get(key)
        if data:
            decoded = json.loads(data)
            return model(**decoded) if model and issubclass(model, BaseModel) else decoded
        return None

    def set(self, key: str, value: any, ttl: int):
        """Cache data with a TTL (seconds)."""
        self.redis_client.setex(key, ttl, json.dumps(value))
