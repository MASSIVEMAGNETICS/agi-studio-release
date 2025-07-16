import importlib
import os

def load_plugins(plugin_dir="plugins"):
    plugins = {}
    for fname in os.listdir(plugin_dir):
        if fname.endswith(".py") and not fname.startswith("_"):
            modname = fname[:-3]
            mod = importlib.import_module(f"plugins.{modname}")
            for attr in dir(mod):
                obj = getattr(mod, attr)
                if isinstance(obj, type) and hasattr(obj, "run"):
                    plugins[attr] = obj
    return plugins
