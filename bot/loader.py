import os, importlib

loaded = {}

def load_plugins(dp):
    for file in os.listdir("plugins"):
        if file.endswith(".py"):
            name = file[:-3]
            module = importlib.import_module(f"plugins.{name}")
            loaded[name] = module

            if hasattr(module, "register"):
                module.register(dp)

def reload_plugin(name, dp):
    if name in loaded:
        importlib.reload(loaded[name])
        if hasattr(loaded[name], "register"):
            loaded[name].register(dp)
