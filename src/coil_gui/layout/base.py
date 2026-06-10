from typing import Any
from abc import ABC, abstractmethod
from .constraints import Size

class Layout(ABC):
    @abstractmethod
    def measure(self, container: Any, available_w: float, available_h: float) -> Size:
        pass

    @abstractmethod
    def arrange(self, container: Any, x: float, y: float, w: float, h: float) -> None:
        pass
