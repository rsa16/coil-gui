import pygame
from typing import Optional, Callable, Any
from ..core.widget import Widget
from ..utils.color import parse_color
from ..utils.layout import set_default_size

class Checkbox(Widget):
    def __init__(self, checked: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._checked = checked

        self.on_change: Optional[Callable[[bool], None]] = kwargs.get("on_change")

        set_default_size(self, 24, 24)

    @property
    def checked(self) -> bool:
        return self._checked

    @checked.setter
    def checked(self, val: bool):
        if self._checked != val:
            self._checked = val
            if self.on_change:
                self.on_change(self._checked)
            self.mark_render_dirty()

    def process_event(self, event: pygame.event.Event, offset_x: float = 0, offset_y: float = 0) -> bool:
        if not self.visible:
            return False

        abs_x = offset_x + self.layout_x
        abs_y = offset_y + self.layout_y
        rect = pygame.Rect(abs_x, abs_y, self.layout_width, self.layout_height)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and rect.collidepoint(event.pos):
                self.checked = not self.checked
                return True

        return super().process_event(event, offset_x, offset_y)

    def draw(self, surface: pygame.Surface):
        # Draw box
        bg_color = parse_color(self.style.get("background_color", "#333333"))
        border_color = parse_color(self.style.get("border_color", "#666666"))
        border_width = 2

        pygame.draw.rect(surface, bg_color, surface.get_rect())
        pygame.draw.rect(surface, border_color, surface.get_rect(), width=border_width)

        # Draw checkmark
        if self._checked:
            check_color = parse_color(self.style.get("check_color", "#0078d7"))
            padding = 4
            inner_rect = surface.get_rect().inflate(-padding*2, -padding*2)
            pygame.draw.rect(surface, check_color, inner_rect)

            # Or draw an actual checkmark? Let's do a simple cross for now or solid box
            # A solid box is fine for a simple UI.
