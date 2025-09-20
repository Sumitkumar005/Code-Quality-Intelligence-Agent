

# Convenience functions for backward compatibility
def get_cache(key):
    return cache.get(key)

def set_cache(key, value, ttl=None):
    return cache.set(key, value, ttl)

def delete_cache(key):
    return cache.delete(key)
