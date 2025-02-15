# plugins/plugin_manager.py

import inspect
import importlib
import os
from typing import Protocol, Any, Dict, Optional

class Tool(Protocol):
    """
    Base interface for any plugin tool.
    Each plugin must define:
      - a unique name (str)
      - a description (str)
      - a run(...) method to do the actual work
    """
    name: str
    description: str

    def run(self, *args, **kwargs) -> Any:
        ...

# We'll keep a registry (dictionary) of tool_name -> tool_class (or instance)
TOOLS_REGISTRY: Dict[str, Tool] = {}

def register_tool(tool: Tool):
    """
    Register a tool instance or class into the global TOOLS_REGISTRY.
    """
    if tool.name in TOOLS_REGISTRY:
        raise ValueError(f"Tool '{tool.name}' is already registered.")
    TOOLS_REGISTRY[tool.name] = tool

def load_plugins(plugins_dir: str):
    """
    Dynamically import all .py files in 'plugins_dir' (except __init__.py and plugin_manager.py).
    Each file can define one or more classes or objects implementing 'Tool'.
    Then call 'register_tool(...)' for each.
    """
    for filename in os.listdir(plugins_dir):
        # Skip non-.py files or special files
        if not filename.endswith(".py"):
            continue
        if filename in ["__init__.py", "plugin_manager.py"]:
            continue

        module_name = filename[:-3]  # strip .py
        module_path = f"{plugins_dir.replace('/', '.')}.{module_name}"

        # Dynamically import
        module = importlib.import_module(module_path)

        # Search for any variables/classes that match the 'Tool' Protocol
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) or inspect.isfunction(obj):
                # We'll do a very loose check: does 'obj' have the attributes 'name', 'description', and 'run'?
                if hasattr(obj, "name") and hasattr(obj, "description") and hasattr(obj, "run"):
                    # Attempt to register it
                    # If it's a class, instantiate it. If it's already an instance, use as is.
                    if inspect.isclass(obj):
                        tool_instance = obj()
                    else:
                        tool_instance = obj

                    # Must have a 'name' attribute
                    if not getattr(tool_instance, "name", None):
                        continue

                    register_tool(tool_instance)

def get_tool_by_name(name: str) -> Optional[Tool]:
    """
    Retrieve a tool by its name from the registry.
    """
    return TOOLS_REGISTRY.get(name)
