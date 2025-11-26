import pytest

from app.utils import cache


class FakeRedis:
    def __init__(self):
        self.store = {}

    def set(self, key, value, ex=None):
        # emulate redis storing strings
        self.store[key] = value
        return True

    def get(self, key):
        return self.store.get(key)


def test_cache_set_get_with_fake_redis(monkeypatch):
    """Ensure cache_set stores JSON-serialised value and cache_get returns it."""
    fake = FakeRedis()
    # patch get_redis used by the cache module to return our fake client
    monkeypatch.setattr(cache, "get_redis", lambda: fake)

    # set and get a dict
    cache.cache_set("test:key:dict", {"a": 1, "b": "c"}, ttl=5)
    val = cache.cache_get("test:key:dict")
    assert isinstance(val, dict)
    assert val["a"] == 1 and val["b"] == "c"

    # set and get a list
    cache.cache_set("test:key:list", [1, 2, 3], ttl=5)
    val2 = cache.cache_get("test:key:list")
    assert isinstance(val2, list)
    assert val2 == [1, 2, 3]


def test_cache_no_raise_on_redis_error(monkeypatch):
    """If Redis client acquisition raises, cache functions should not raise.

    This verifies the defensive fallback in the cache wrapper.
    """

    def bad_get_redis():
        raise RuntimeError("redis unavailable")

    monkeypatch.setattr(cache, "get_redis", bad_get_redis)

    # cache_set should swallow errors and not raise
    cache.cache_set("some:key", {"x": 1}, ttl=1)

    # cache_get should return None when redis errors
    assert cache.cache_get("some:key") is None
