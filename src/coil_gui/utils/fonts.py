import pygame
from typing import Dict, Tuple

_font_cache: Dict[Tuple[str, int], pygame.font.Font] = {}

def get_font(name: str, size: int) -> pygame.font.Font:
    """Get a font from the cache or load it if not present."""
    if not pygame.font.get_init():
        pygame.font.init()

    key = (name, size)
    if key not in _font_cache:
        # If it's a file path, load it. Otherwise, match sysfont.
        if name is not None and (name.endswith(".ttf") or name.endswith(".otf")):
            try:
                _font_cache[key] = pygame.font.Font(name, size)
            except FileNotFoundError:
                _font_cache[key] = pygame.font.SysFont(None, size)
        else:
            _font_cache[key] = pygame.font.SysFont(name, size)

    return _font_cache[key]
