import pygame
from typing import Optional, Callable, Any
from ..core.widget import Widget
from ..utils.color import parse_color
from ..utils.layout import set_default_size

class ToggleSwitch(Widget):
    def __init__(self, checked: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._checked = checked
        self._thumb_pos = 1.0 if checked else 0.0

        self.on_change: Optional[Callable[[bool], None]] = kwargs.get("on_change")

        set_default_size(self, 50, 25)

    @property
    def checked(self) -> bool:
        return self._checked

    @checked.setter
    def checked(self, val: bool):
        if self._checked != val:
            self._checked = val
            target = 1.0 if val else 0.0
            self.animate("_thumb_pos", target, duration=0.2, easing="ease_out_quad")
            if self.on_change:
                self.on_change(self._checked)
            self.mark_render_dirty()

    @property
    def _thumb_pos(self) -> float:
        return self.__thumb_pos

    @_thumb_pos.setter
    def _thumb_pos(self, val: float):
        self.__thumb_pos = val
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
        # Draw track
        track_color_off = parse_color(self.style.get("track_color_off", "#444444"))
        track_color_on = parse_color(self.style.get("track_color_on", "#0078d7"))

        # Interpolate track color using thumb_pos
        c_off = pygame.Color(track_color_off)
        c_on = pygame.Color(track_color_on)
        current_track_color = c_off.lerp(c_on, self._thumb_pos)

        radius = int(self.layout_height // 2)
        pygame.draw.rect(surface, current_track_color, (0, 0, self.layout_width, self.layout_height), border_radius=radius)

        # Draw thumb
        thumb_color = parse_color(self.style.get("thumb_color", "#ffffff"))
        thumb_radius = radius - 2
        thumb_x = 2 + self._thumb_pos * (self.layout_width - 2 * thumb_radius - 4)
        pygame.draw.circle(surface, thumb_color, (int(thumb_x + thumb_radius), radius), thumb_radius)
