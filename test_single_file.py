def bad_function():
    password = "hardcoded123"  # Security issue
    api_key = "secret_key_here"  # Another security issue
    
    # Performance issue - nested loops
    for i in range(1000):
        for j in range(1000):
            for k in range(100):  # Triple nested!
                pass
    
    # Code quality issue - function too long
    print("line 1")
    print("line 2")
    print("line 3")
    # ... imagine 50+ more lines
    
    return "done"

# Missing docstring - documentation issue
class BadClass:
    def method_with_too_many_params(self, a, b, c, d, e, f, g, h):  # Too many params
        pass