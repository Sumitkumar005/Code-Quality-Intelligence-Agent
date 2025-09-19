# Test file with performance issues for CLI testing

import time
import requests
import json

# PERFORMANCE ISSUE: Synchronous operations in loop
def fetch_user_data_slow(user_ids):
    results = []
    for user_id in user_ids:
        # Blocking HTTP request in loop
        response = requests.get(f"https://api.example.com/users/{user_id}")
        results.append(response.json())
        time.sleep(0.1)  # Additional delay
    return results

# PERFORMANCE ISSUE: Inefficient data structure usage
def find_duplicates_slow(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates

# PERFORMANCE ISSUE: Memory leak potential
class DataProcessor:
    def __init__(self):
        self.cache = {}
        self.large_data = []
    
    def process_data(self, data):
        # Never clears cache - potential memory leak
        key = str(data)
        if key not in self.cache:
            # Stores large objects without cleanup
            processed = self._expensive_operation(data)
            self.cache[key] = processed
            self.large_data.append(processed)
        return self.cache[key]
    
    def _expensive_operation(self, data):
        # Simulates expensive operation
        result = []
        for i in range(10000):
            result.append(data * i)
        return result

# PERFORMANCE ISSUE: Inefficient string concatenation
def build_large_string(items):
    result = ""
    for item in items:
        result += str(item) + "\n"  # Inefficient string concatenation
    return result

# PERFORMANCE ISSUE: Nested loops with high complexity
def matrix_multiplication_slow(matrix_a, matrix_b):
    rows_a, cols_a = len(matrix_a), len(matrix_a[0])
    rows_b, cols_b = len(matrix_b), len(matrix_b[0])
    
    if cols_a != rows_b:
        raise ValueError("Cannot multiply matrices")
    
    result = []
    for i in range(rows_a):
        row = []
        for j in range(cols_b):
            sum_val = 0
            for k in range(cols_a):
                # Inefficient nested loops
                sum_val += matrix_a[i][k] * matrix_b[k][j]
                # Additional unnecessary operations
                temp = sum_val * 1.0
                temp = temp / 1.0
                sum_val = temp
            row.append(sum_val)
        result.append(row)
    return result

# CODE QUALITY ISSUE: No documentation, poor naming
def f(x, y, z):
    a = x + y
    b = a * z
    c = b / 2
    d = c ** 2
    return d

# SECURITY + PERFORMANCE: Unsafe and slow file operations
def process_files_unsafe(directory):
    import os
    results = []
    for filename in os.listdir(directory):
        # SECURITY: No path validation
        filepath = directory + "/" + filename
        
        # PERFORMANCE: Synchronous file operations
        with open(filepath, 'r') as f:
            content = f.read()
            
        # PERFORMANCE: Inefficient processing
        lines = content.split('\n')
        for line in lines:
            for char in line:
                if char.isdigit():
                    results.append(int(char))
    
    return results