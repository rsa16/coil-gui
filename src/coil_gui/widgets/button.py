import pygame
from typing import Optional, Callable, Any
from ..core.container import Container
from .label import Label
from ..layout.flex import FlexLayout, JustifyContent, AlignItems
from ..utils.color import parse_color
from ..utils.layout import resolve_padding_tuple

class Button(Container):
    def __init__(self, text: str, on_click: Optional[Callable[[], None]] = None, **kwargs):
        # Default layout for button: center content
        layout = kwargs.pop(
            "layout",
            FlexLayout(justify=JustifyContent.CENTER, align=AlignItems.CENTER, padding=10),
        )
        super().__init__(layout=layout, **kwargs)

        self.on_click = on_click

        self.label = Label(text)
        self.add_child(self.label)

        self._pressed = False

    @property
    def text(self) -> str:
        return self.label.text

    @text.setter
    def text(self, value: str):
        self.label.text = value

    @property
    def disabled(self) -> bool:
        return "disabled" in self.state_flags

    @disabled.setter
    def disabled(self, value: bool):
        if value:
            self.state_flags.add("disabled")
        else:
            self.state_flags.discard("disabled")
        self.mark_render_dirty()

    def perform_layout(self):
        if isinstance(self.layout, FlexLayout):
            p = self.style.get("padding", self.layout.padding)
            # Handle tuple padding from style
            if isinstance(p, tuple):
                pt, pb, pl, pr = resolve_padding_tuple(p)
                self.layout.padding_top = pt
                self.layout.padding_bottom = pb
                self.layout.padding_left = pl
                self.layout.padding_right = pr
            else:
                self.layout.padding_top = self.style.get("padding_top", p)
                self.layout.padding_bottom = self.style.get("padding_bottom", p)
                self.layout.padding_left = self.style.get("padding_left", p)
                self.layout.padding_right = self.style.get("padding_right", p)

        super().perform_layout()

    def process_event(self, event: pygame.event.Event, offset_x: float = 0, offset_y: float = 0) -> bool:
        if not self.visible:
            return False

        abs_x = offset_x + self.layout_x
        abs_y = offset_y + self.layout_y

        # Calculate the actual top-left based on origin
        draw_x = abs_x - (self.origin[0] * self.layout_width)
        draw_y = abs_y - (self.origin[1] * self.layout_height)

        rect = pygame.Rect(draw_x, draw_y, self.layout_width, self.layout_height)

        if self.disabled:
            # Still let children process if needed, but usually buttons are atomic
            return super().process_event(event, offset_x, offset_y)

        # Handle button-specific logic
        consumed = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and rect.collidepoint(event.pos):
                self._pressed = True
                self.state_flags.add("active")
                self.mark_render_dirty()
                consumed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                was_pressed = self._pressed
                self._pressed = False
                if "active" in self.state_flags:
                    self.state_flags.discard("active")
                    self.mark_render_dirty()

                if was_pressed and rect.collidepoint(event.pos):
                    if self.on_click:
                        self.on_click()
                    consumed = True

        # Always call super to handle hover state and child events
        # We pass consumed as well? No, super handles its own.
        super_consumed = super().process_event(event, offset_x, offset_y)
        return consumed or super_consumed

    def draw(self, surface: pygame.Surface):
        # We don't call super().draw(surface) because we want custom border support

        bg_color_val = self.style.get("background_color")
        border_color_val = self.style.get("border_color")
        border_width = self.style.get("border_width", 0)
        border_radius = self.style.get("border_radius", 0)

        rect = surface.get_rect()

        if bg_color_val:
            bg_color = parse_color(bg_color_val)
            if border_radius > 0:
                pygame.draw.rect(surface, bg_color, rect, border_radius=int(border_radius))
            else:
                surface.fill(bg_color)

        if border_color_val and border_width > 0:
            border_color = parse_color(border_color_val)
            pygame.draw.rect(surface, border_color, rect, width=int(border_width), border_radius=int(border_radius))

        # Update label color if button has a color style defined for the current state
        label_color = self.style.get("color")
        if label_color:
            self.label.style.color = label_color
