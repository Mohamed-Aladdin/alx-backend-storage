#!/usr/bin/env python3
"""Task 5 Module"""


import redis
import requests
from typing import Callable
from functools import wraps


r = redis.Redis()


def url_access_count(method: Callable) -> Callable:
    """decorator to track how many times a particular URL
    was accessed inthe key "count:{url}" and cache
    the result with an expiration time of 10 seconds.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        """wrapper function"""
        r.incr(f'count:{url}')
        result = r.get(f'result:{url}')
        if result:
            return result.decode("utf-8")
        result = method(url)
        r.set(f'count:{url}', 0)
        r.setex(f'result:{url}', 10, result)
        return result
    return wrapper


@url_access_count
def get_page(url: str) -> str:
    """method that uses the requests module to obtain
    the HTML content of a particular URL and returns it.
    """
    results = requests.get(url)
    return results.text


# if __name__ == "__main__":
#     get_page('http://slowwly.robertomurray.co.uk')
