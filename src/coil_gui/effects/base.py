import pygame
from typing import Any
from abc import ABC, abstractmethod

class Effect(ABC):
    @abstractmethod
    def process(self, surface: pygame.Surface, widget: Any) -> pygame.Surface:
        """Return a new (or modified) surface.
        For simplicity, assume the returned surface might be larger.
        """
        pass
