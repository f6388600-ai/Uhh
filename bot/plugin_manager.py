import os

DISABLED_FILE = "disabled.txt"

def get_disabled():
    if not os.path.exists(DISABLED_FILE):
        return []
    with open(DISABLED_FILE, "r") as f:
        return f.read().splitlines()

def disable(name):
    data = get_disabled()
    if name not in data:
        data.append(name)
    with open(DISABLED_FILE, "w") as f:
        f.write("\n".join(data))

def enable(name):
    data = get_disabled()
    if name in data:
        data.remove(name)
    with open(DISABLED_FILE, "w") as f:
        f.write("\n".join(data))

def is_disabled(name):
    return name in get_disabled()
