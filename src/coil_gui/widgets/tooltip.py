import pygame
from typing import Optional, Any
from ..core.widget import Widget
from ..core.container import Container
from ..layout.flex import FlexLayout, FlexDirection, AlignItems
from ..utils.color import parse_color
from ..utils.layout import set_default_size
from .label import Label


class Tooltip(Widget):
    def __init__(self, text: str = "", target: Optional[Widget] = None, **kwargs):
        super().__init__(**kwargs)
        self._text = text
        self._target = target
        self._delay = kwargs.get("delay", 0.5)
        self._hover_timer = 0.0
        self._showing = False

        # Tooltip label
        self.tooltip_label = Label(text, font_size=14, color="#ffffff", padding=5)
        self.tooltip_label.visible = False
        self.tooltip_label.z_index = 999
        self.add_child(self.tooltip_label)

        set_default_size(self, 0, 0)

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value
        self.tooltip_label.text = value

    @property
    def target(self) -> Optional[Widget]:
        return self._target

    @target.setter
    def target(self, widget: Optional[Widget]):
        self._target = widget

    def update_animations(self, dt: float):
        super().update_animations(dt)
        if not self._target:
            return

        if "hover" in self._target.state_flags:
            self._hover_timer += dt
            if self._hover_timer >= self._delay and not self._showing:
                self._showing = True
                self.tooltip_label.visible = True
                self.mark_render_dirty()
        else:
            if self._showing:
                self._showing = False
                self.tooltip_label.visible = False
                self.mark_render_dirty()
            self._hover_timer = 0.0

    def render(self, surface: pygame.Surface, dirty_rects: list, offset_x: float = 0, offset_y: float = 0):
        if not self._showing or not self._target:
            return

        # Position tooltip near the target
        target_abs = self._target.get_absolute_position()
        tip_x = target_abs[0] + self._target.layout_width / 2 - self.tooltip_label.layout_width / 2
        tip_y = target_abs[1] - self.tooltip_label.layout_height - 5

        # Draw background
        bg_color = parse_color("#333333")
        border_color = parse_color("#555555")
        tw = self.tooltip_label.layout_width
        th = self.tooltip_label.layout_height
        pygame.draw.rect(surface, bg_color, (tip_x, tip_y, tw, th))
        pygame.draw.rect(surface, border_color, (tip_x, tip_y, tw, th), width=1)

        # Draw label
        self.tooltip_label.render(surface, dirty_rects, tip_x, tip_y)

    def draw(self, surface: pygame.Surface):
        pass  # Tooltip draws in render()
