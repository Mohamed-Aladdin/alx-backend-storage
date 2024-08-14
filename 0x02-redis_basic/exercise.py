#!/usr/bin/env python3
"""Task 0 Module"""


import redis
import uuid
from functools import wraps
from typing import Union, Callable, Optional


def count_calls(method: Callable) -> Callable:
    """Create and return function that increments the count
    for that keyevery time the method is called and
    returns the value returned by the original method.
    """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper for the decorated fn."""
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper

def call_history(method: Callable) -> Callable:
    """decorator to store the history of inputs
    and outputs for a particular function.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper for the decorated fn."""
        input = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", input)
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(method.__qualname__ + ":outputs", output)
        return output
    return wrapper

def replay(fn: Callable):
    """method to display the history of calls of a particular function."""
    r = redis.Redis()
    fn_name = fn.__qualname__
    value = r.get(fn_name)

    try:
        value = int(value.decode("utf-8"))
    except Exception:
        value = 0

    print("{} was called {} times:".format(fn_name, value))
    inputs = r.lrange("{}:inputs".format(fn_name), 0, -1)
    outputs = r.lrange("{}:outputs".format(fn_name), 0, -1)

    for input, output in zip(inputs, outputs):
        try:
            input = input.decode("utf-8")
        except Exception:
            input = ""

        try:
            output = output.decode("utf-8")
        except Exception:
            output = ""

        print("{}(*{}) -> {}".format(fn_name, input, output))


class Cache:
    """To cache using redis"""
    def __init__(self) -> None:
        """Constructor init"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """method should generate a random key (e.g. using uuid) store
        the input data in Redis using the random key and return the key.
        """
        key = uuid.uuid4()
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable[[bytes], Union[str, bytes, int, float]]] = None) -> Optional[Union[str, int, float, bytes]]:
        """method that take a key string argument and an optional
        Callable argument named fn. This callable will be used to
        convert the data back to the desired format.
        """
        data = self._redis.get(key)
        if data is not None and fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        """method that decodes bytes to string"""
        return self.get(key, lambda x: x.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """method that decodes bytes to integer"""
        return self.get(key, lambda x: int(x))
