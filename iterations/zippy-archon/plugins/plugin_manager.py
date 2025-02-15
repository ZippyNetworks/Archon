# zippy-archon/plugins/plugin_manager.py

import os
import importlib
import inspect
from typing import Protocol, Dict

class Tool(Protocol):
    name: str
    description: str
    def run(self, *args, **kwargs) -> str:
        ...

TOOLS_REGISTRY: Dict[str, Tool] = {}

def register_tool(tool: Tool):
    if tool.name in TOOLS_REGISTRY:
        raise ValueError(f"Tool '{tool.name}' is already registered.")
    TOOLS_REGISTRY[tool.name] = tool

def load_plugins(plugins_dir: str):
    """
    Dynamically import .py files in 'plugins_dir' 
    and register any classes/objects that match our Tool interface.
    """
    for filename in os.listdir(plugins_dir):
        if not filename.endswith(".py"):
            continue
        if filename in ["__init__.py", "plugin_manager.py"]:
            continue

        module_name = filename[:-3]
        module = importlib.import_module(f"plugins.{module_name}")

        for name, obj in inspect.getmembers(module):
            if hasattr(obj, "name") and hasattr(obj, "run"):
                # If it's a class, instantiate it
                instance = obj() if inspect.isclass(obj) else obj
                register_tool(instance)
