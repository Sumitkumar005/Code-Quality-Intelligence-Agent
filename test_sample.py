#!/usr/bin/env python3
"""
Sample Python file for testing analysis
"""

import os
import json

def hello_world():
    """A simple function"""
    print("Hello, World!")
    return "Hello"
password = "summer2024"  # Example password, should be handled securely
class TestClass:
    """A test class"""

    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, {self.name}!"

if __name__ == "__main__":
    obj = TestClass("Alice")
    print(obj.greet())
