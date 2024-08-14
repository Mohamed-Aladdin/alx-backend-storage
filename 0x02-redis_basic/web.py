#!/usr/bin/env python3
"""Task 5 Module"""


import redis
import requests
from functools import wraps


r = redis.Redis()


def url_access_count(method):
    """decorator to track how many times a particular URL
    was accessed inthe key "count:{url}" and cache
    the result with an expiration time of 10 seconds.
    """
    @wraps(method)
    def wrapper(url):
        """wrapper for the decorated fn."""
        key = "cached:" + url
        cached_value = r.get(key)

        if cached_value:
            return cached_value.decode("utf-8")

        key_count = "count:" + url
        html_content = method(url)

        r.incr(key_count)
        r.set(key, html_content, ex=10)
        r.expire(key, 10)
        return html_content
    return wrapper


@url_access_count
def get_page(url: str) -> str:
    """method that uses the requests module to obtain
    the HTML content of a particular URL and returns it.
    """
    res = requests.get(url)
    return res.text


if __name__ == "__main__":
    get_page('http://slowwly.robertomurray.co.uk')
