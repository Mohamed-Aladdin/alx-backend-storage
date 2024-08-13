#!/usr/bin/env python3
"""Task 8 Module"""


def list_all(mongo_collection):
    """Write a Python function that lists all documents in a collection"""
    
    return [doc for doc in mongo_collection.find()]
