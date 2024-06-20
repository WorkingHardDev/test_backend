import asyncio
from functools import wraps, update_wrapper
import cachetools


def async_cached(cache, key=cachetools.keys.hashkey, lock=None):
    '''
    Async decorator that caches the result of a function inside an async function.
    '''
    if lock is None:
        lock = asyncio.Lock()

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = key(*args, **kwargs)
            async with lock:
                if cache_key in cache:
                    return cache[cache_key]
                else:
                    result = await func(*args, **kwargs)
                    cache[cache_key] = result
                    return result

        return wrapper

    return decorator
