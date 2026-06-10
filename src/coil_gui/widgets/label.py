import pygame
from typing import Optional

from ..core.widget import Widget
from ..utils.fonts import get_font
from ..utils.color import parse_color

class Label(Widget):
    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs)
        self._text = text
        self._update_size()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        if self._text != value:
            self._text = value
            self._update_size()
            self.mark_render_dirty()
            self.mark_layout_dirty()

    def _update_size(self):
        font_name = self.style.get('font_name', None)
        font_size = self.style.get('font_size', 24)
        font = get_font(font_name, font_size)

        w, h = font.size(self._text)
        self.width = w
        self.height = h

    def on_manager_changed(self):
        super().on_manager_changed()
        self._update_size()

    def measure(self, available_w: float, available_h: float) -> Any:
        from ..layout.constraints import Size
        self._update_size()
        return Size(w=self.constraints.clamp_w(self.width), h=self.constraints.clamp_h(self.height))

    def perform_layout(self):
        self._update_size()
        super().perform_layout()

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        font_name = self.style.get('font_name', None)
        font_size = self.style.get('font_size', 24)
        color_val = self.style.get('color', '#ffffff')

        font = get_font(font_name, font_size)
        color = parse_color(color_val)

        text_surf = font.render(self._text, True, color)

        # Simple centering or top-left. For now, top-left
        surface.blit(text_surf, (0, 0))
