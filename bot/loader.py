import os, importlib
from plugin_manager import is_disabled

loaded = {}

def load_plugins(dp):
    for file in os.listdir("plugins"):
        if file.endswith(".py"):
            name = file[:-3]

            if is_disabled(name):
                print(f"🚫 Skipped: {name}")
                continue

            module = importlib.import_module(f"plugins.{name}")
            loaded[name] = module

            if hasattr(module, "register"):
                module.register(dp)
