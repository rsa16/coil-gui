import pygame
from typing import Optional, Callable, Any, List
from ..core.widget import Widget
from ..utils.color import parse_color
from ..utils.layout import set_default_size

class RadioButton(Widget):
    _groups: dict[str, List['RadioButton']] = {}

    def __init__(self, group: str, checked: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.group = group
        self._checked = checked

        if group not in RadioButton._groups:
            RadioButton._groups[group] = []
        RadioButton._groups[group].append(self)

        self.on_change: Optional[Callable[[bool], None]] = kwargs.get("on_change")

        set_default_size(self, 24, 24)

    @property
    def checked(self) -> bool:
        return self._checked

    @checked.setter
    def checked(self, val: bool):
        if val:
            # Uncheck others in group
            for rb in RadioButton._groups.get(self.group, []):
                if rb != self and rb.checked:
                    rb._checked = False
                    rb.mark_render_dirty()
                    if rb.on_change:
                        rb.on_change(False)

            if not self._checked:
                self._checked = True
                self.mark_render_dirty()
                if self.on_change:
                    self.on_change(True)
        else:
            if self._checked:
                self._checked = False
                self.mark_render_dirty()
                if self.on_change:
                    self.on_change(False)

    def process_event(self, event: pygame.event.Event, offset_x: float = 0, offset_y: float = 0) -> bool:
        if not self.visible:
            return False

        abs_x = offset_x + self.layout_x
        abs_y = offset_y + self.layout_y
        rect = pygame.Rect(abs_x, abs_y, self.layout_width, self.layout_height)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and rect.collidepoint(event.pos):
                self.checked = True # Radio button can only be checked by click, not unchecked
                return True

        return super().process_event(event, offset_x, offset_y)

    def draw(self, surface: pygame.Surface):
        # Draw circle
        bg_color = parse_color(self.style.get("background_color", "#333333"))
        border_color = parse_color(self.style.get("border_color", "#666666"))

        radius = min(self.layout_width, self.layout_height) // 2
        center = (self.layout_width // 2, self.layout_height // 2)

        pygame.draw.circle(surface, bg_color, center, radius)
        pygame.draw.circle(surface, border_color, center, radius, width=2)

        # Draw dot
        if self._checked:
            dot_color = parse_color(self.style.get("dot_color", "#0078d7"))
            pygame.draw.circle(surface, dot_color, center, radius - 6)
