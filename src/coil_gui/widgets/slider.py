import pygame
from typing import Optional, Callable, Any
from ..core.widget import Widget
from ..utils.color import parse_color
from ..utils.layout import set_default_size

class Slider(Widget):
    def __init__(self, value: float = 0.0, min_val: float = 0.0, max_val: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self._value = value
        self._min_val = min_val
        self._max_val = max_val
        self._dragging = False

        self.on_change: Optional[Callable[[float], None]] = kwargs.get("on_change")

        set_default_size(self, 200, 20)

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, val: float):
        val = max(self._min_val, min(self._max_val, val))
        if self._value != val:
            self._value = val
            self.mark_render_dirty()
            if self.on_change:
                self.on_change(self._value)

    def _get_thumb_rect(self) -> pygame.Rect:
        # Calculate thumb position
        range_val = self._max_val - self._min_val
        if range_val == 0:
            percent = 0
        else:
            percent = (self._value - self._min_val) / range_val

        thumb_width = 10
        thumb_height = self.layout_height
        thumb_x = percent * (self.layout_width - thumb_width)
        return pygame.Rect(thumb_x, 0, thumb_width, thumb_height)

    def process_event(self, event: pygame.event.Event, offset_x: float = 0, offset_y: float = 0) -> bool:
        if not self.visible:
            return False

        abs_x = offset_x + self.layout_x
        abs_y = offset_y + self.layout_y
        rect = pygame.Rect(abs_x, abs_y, self.layout_width, self.layout_height)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and rect.collidepoint(event.pos):
                self._dragging = True
                self._update_value_from_pos(event.pos[0] - abs_x)
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self._dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self._dragging:
                self._update_value_from_pos(event.pos[0] - abs_x)
                return True

        return super().process_event(event, offset_x, offset_y)

    def _update_value_from_pos(self, local_x: float):
        percent = max(0, min(1, local_x / self.layout_width))
        self.value = self._min_val + percent * (self._max_val - self._min_val)

    def draw(self, surface: pygame.Surface):
        # Draw track
        track_color = parse_color(self.style.get("track_color", "#444444"))
        track_height = 4
        track_y = (self.layout_height - track_height) // 2
        pygame.draw.rect(surface, track_color, (0, track_y, self.layout_width, track_height))

        # Draw filled part
        fill_color = parse_color(self.style.get("fill_color", "#0078d7"))
        range_val = self._max_val - self._min_val
        percent = (self._value - self._min_val) / range_val if range_val != 0 else 0
        pygame.draw.rect(surface, fill_color, (0, track_y, self.layout_width * percent, track_height))

        # Draw thumb
        thumb_rect = self._get_thumb_rect()
        thumb_color = parse_color(self.style.get("thumb_color", "#ffffff"))
        pygame.draw.rect(surface, thumb_color, thumb_rect)
