import pygame
from typing import Optional, Union
from ..core.widget import Widget
from ..utils.layout import set_default_size

class Image(Widget):
    def __init__(self, source: Union[str, pygame.Surface], **kwargs):
        super().__init__(**kwargs)
        self._source = source
        self._image: Optional[pygame.Surface] = None
        self._original_image: Optional[pygame.Surface] = None

        if isinstance(source, pygame.Surface):
            self._original_image = source
            self._update_image()
        elif isinstance(source, str):
            self._load_image(source)

    def _load_image(self, path: str):
        try:
            self._original_image = pygame.image.load(path).convert_alpha()
            self._update_image()
        except pygame.error as e:
            print(f"Failed to load image {path}: {e}")
            self._original_image = pygame.Surface((32, 32))
            self._original_image.fill((255, 0, 255)) # Pink fallback
            self._update_image()

    def _update_image(self):
        if self._original_image:
            w = self.width if self.width > 0 else self._original_image.get_width()
            h = self.height if self.height > 0 else self._original_image.get_height()

            if w != self._original_image.get_width() or h != self._original_image.get_height():
                self._image = pygame.transform.smoothscale(self._original_image, (int(w), int(h)))
            else:
                self._image = self._original_image

            set_default_size(self, w, h)

            self.mark_render_dirty()

    @property
    def source(self) -> Union[str, pygame.Surface]:
        return self._source

    @source.setter
    def source(self, value: Union[str, pygame.Surface]):
        self._source = value
        if isinstance(value, pygame.Surface):
            self._original_image = value
            self._update_image()
        elif isinstance(value, str):
            self._load_image(value)

    def on_layout(self):
        super().on_layout()
        # If layout changed size, we might need to rescale
        if self.layout_width > 0 and self.layout_height > 0:
            if self._original_image:
                if (int(self.layout_width), int(self.layout_height)) != self._image.get_size():
                    self._image = pygame.transform.smoothscale(self._original_image, (int(self.layout_width), int(self.layout_height)))
                    self.mark_render_dirty()

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        if self._image:
            surface.blit(self._image, (0, 0))
