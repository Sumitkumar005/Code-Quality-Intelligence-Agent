file_path = "app/core/cache.py"

with open(file_path, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

print("".join(lines[-30:]))
