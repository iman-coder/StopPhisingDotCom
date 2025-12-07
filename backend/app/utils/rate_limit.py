from typing import Callable, Optional
import time
from fastapi import Request, HTTPException, Depends
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.utils.cache import get_redis

# Lua token-bucket script (atomic)
LUA_TOKEN_BUCKET = r"""
local key = KEYS[1]
local rate = tonumber(ARGV[1])        -- tokens per second
local capacity = tonumber(ARGV[2])    -- bucket size
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local data = redis.call('HMGET', key, 'tokens', 'last')
local tokens = tonumber(data[1]) or capacity
local last = tonumber(data[2]) or 0
local delta = math.max(0, now - last)
local refill = delta * rate
tokens = math.min(capacity, tokens + refill)
local allowed = tokens >= requested
if allowed then
  tokens = tokens - requested
  redis.call('HMSET', key, 'tokens', tokens, 'last', now)
  redis.call('EXPIRE', key, math.ceil(math.max(60, capacity / rate * 2)))
  return 1
else
  redis.call('HMSET', key, 'tokens', tokens, 'last', now)
  redis.call('EXPIRE', key, math.ceil(math.max(60, capacity / rate * 2)))
  return 0
end
"""


class RateLimiter:
    def __init__(self, redis_client=None):
        self.redis = redis_client or get_redis()
        self._sha = None

    def _load(self):
        if self._sha is None:
            try:
                self._sha = self.redis.script_load(LUA_TOKEN_BUCKET)
            except Exception:
                self._sha = None
        return self._sha

    def allow(self, key: str, rate: float, capacity: int = 1, requested: int = 1) -> bool:
        """Attempt to consume `requested` tokens from key. rate = tokens/sec, capacity = bucket size.
        Returns True if allowed; False if rate limit exceeded. On Redis errors, returns True (fail-open).
        """
        sha = self._load()
        now = time.time()
        if sha is None:
            # Redis script load failed or Redis unreachable — fail-open
            return True
        try:
            res = self.redis.evalsha(sha, 1, key, str(rate), str(capacity), str(now), str(requested))
            return bool(res)
        except Exception:
            # fail-open to avoid accidental outage if Redis is flaky
            return True


def rate_limit_dep(prefix: str, limit_per_minute: int, burst: int = 1, key_fn: Optional[Callable[[Request], str]] = None):
    """Return a FastAPI dependency that enforces a token-bucket per key.

    prefix: identifies the limiter purpose (used in redis key)
    limit_per_minute: allowed tokens per minute
    burst: bucket capacity (allows short bursts)
    key_fn: optional function(Request) -> identity string (e.g., user id or IP)
    """
    limiter = RateLimiter()
    rate_per_sec = float(limit_per_minute) / 60.0
    capacity = burst

    async def _dep(request: Request):
        if key_fn:
            try:
                identity = key_fn(request)
            except Exception:
                identity = request.client.host
        else:
            identity = request.client.host
        key = f"rl:{prefix}:{identity}"
        allowed = limiter.allow(key, rate_per_sec, capacity, requested=1)
        if not allowed:
            raise HTTPException(status_code=HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")

    return _dep
