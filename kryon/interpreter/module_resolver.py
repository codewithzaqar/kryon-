import os
from typing import Dict, List

class ModuleResolver:
    def __init__(self):
        self.loaded_modules: Dict[str, bool] = {}
        self.module_objects: Dict[str, Any] = {}
        self.base_path: str = ""

    def set_base_path(self, path: str):
        self.base_path = os.path.dirname(os.path.abspath(path))

    def resolve_path(self, module_name: str) -> str:
        # Simple resolution assume .kry extension and relative to base path
        if not module_name.endswith(".kry"):
            module_name += ".kry"
        return os.path.join(self.base_path, module_name)

    def is_loaded(self, module_name: str) -> bool:
        return module_name in self.loaded_modules

    def mark_loaded(self, module_name: str):
        self.loaded_modules[module_name] = True

    def store_module_object(self, module_name: str, obj: Any):
        self.module_objects[module_name] = obj

    def get_module_object(self, module_name: str) -> Any:
        return self.module_objects.get(module_name)
