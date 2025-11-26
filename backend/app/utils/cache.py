import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0") #might need to be changed for production

try:
    import redis
    _redis_client: Optional[redis.Redis] = None

    def get_redis():
        global _redis_client
        if _redis_client is None:
            _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        return _redis_client

    def cache_set(key: str, value, ttl: int = 60):
        try:
            r = get_redis()
            r.set(key, json.dumps(value), ex=ttl)
        except Exception as e:
            logger.debug("Redis set failed: %s", e)

    def cache_get(key: str):
        try:
            r = get_redis()
            v = r.get(key)
            if v is None:
                return None
            return json.loads(v)
        except Exception as e:
            logger.debug("Redis get failed: %s", e)
            return None

except Exception:
    # If redis library is not available or import fails, provide no-op functions
    logger.warning("`redis` package not available — cache disabled")

    def get_redis():
        return None

    def cache_set(key: str, value, ttl: int = 60):
        return None

    def cache_get(key: str):
        return None
