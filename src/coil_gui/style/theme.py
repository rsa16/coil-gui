from typing import Dict, Any, Optional

class Theme:
    def __init__(self, variables: Optional[Dict[str, Any]] = None):
        self.variables = variables or {}

    def get_var(self, name: str, default: Any = None) -> Any:
        return self.variables.get(name, default)
