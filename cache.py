import redis
import json
from typing import Optional, TypeVar, Type, Any, Union
from pydantic import BaseModel

# Define a generic type variable for type hinting
T = TypeVar("T")


class Cache:
    # Create a Redis client instance connected to localhost on the default port and DB
    redis_client = redis.Redis(host="localhost", port=6379, db=0)

    def get(self, key: str, model: Type[T] = None) -> Optional[Union[T, list[T], Any]]:
        """
        Retrieve cached data for the given key from Redis.

        If a Pydantic model type is provided:
        - Deserialize into a single model instance if the JSON is a dict.
        - Deserialize into a list of model instances if the JSON is a list.

        Otherwise, return the raw deserialized JSON data.

        Args:
            key (str): The Redis key to retrieve.
            model (Type[T], optional): A Pydantic model to deserialize into, if desired.

        Returns:
            Optional[Union[T, list[T], Any]]: The deserialized data, list of models, or None if key is not found.
        """
        data = self.redis_client.get(key)
        if data:
            decoded = json.loads(data)
            if model and issubclass(model, BaseModel):
                if isinstance(decoded, list):
                    return [
                        model(**item) for item in decoded
                    ]  # List of model instances
                return model(**decoded)  # Single model instance
            return decoded
        return None

    def set(self, key: str, value: Any, ttl: int):
        """
        Store a value in Redis with a specific TTL (time to live).

        Args:
            key (str): The Redis key to store under.
            value (Any): The Python data to store (will be serialized to JSON).
            ttl (int): Time to live in seconds.
        """
        if isinstance(value, BaseModel):
            value = value.model_dump()
        elif isinstance(value, list) and all(isinstance(v, BaseModel) for v in value):
            value = [v.model_dump() for v in value]

        self.redis_client.setex(key, ttl, json.dumps(value))
