import pygame
from typing import Optional, Callable, Any
from ..core.widget import Widget
from ..utils.fonts import get_font
from ..utils.color import parse_color
from ..utils.layout import set_default_size

class TextInput(Widget):
    def __init__(self, text: str = "", placeholder: str = "", **kwargs):
        super().__init__(**kwargs)
        self._text = text
        self._placeholder = placeholder
        self._cursor_pos = len(text)
        self._focused = False
        self._cursor_timer = 0.0
        self._cursor_visible = True

        self.on_change: Optional[Callable[[str], None]] = kwargs.get("on_change")
        self.on_submit: Optional[Callable[[str], None]] = kwargs.get("on_submit")

        set_default_size(self, 200, 40)

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        if self._text != value:
            self._text = value
            self._cursor_pos = min(self._cursor_pos, len(value))
            self.mark_render_dirty()
            if self.on_change:
                self.on_change(value)

    def process_event(self, event: pygame.event.Event, offset_x: float = 0, offset_y: float = 0) -> bool:
        if not self.visible:
            return False

        abs_x = offset_x + self.layout_x
        abs_y = offset_y + self.layout_y
        rect = pygame.Rect(abs_x, abs_y, self.layout_width, self.layout_height)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if rect.collidepoint(event.pos):
                self._focused = True
                self.state_flags.add("focused")
                self.mark_render_dirty()
                return True
            else:
                self._focused = False
                self.state_flags.discard("focused")
                self.mark_render_dirty()

        if self._focused and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self._cursor_pos > 0:
                    self.text = self._text[:self._cursor_pos-1] + self._text[self._cursor_pos:]
                    self._cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self._cursor_pos < len(self._text):
                    self.text = self._text[:self._cursor_pos] + self._text[self._cursor_pos+1:]
            elif event.key == pygame.K_LEFT:
                self._cursor_pos = max(0, self._cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self._cursor_pos = min(len(self._text), self._cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self._cursor_pos = 0
            elif event.key == pygame.K_END:
                self._cursor_pos = len(self._text)
            elif event.key == pygame.K_RETURN:
                if self.on_submit:
                    self.on_submit(self._text)
            else:
                if event.unicode and event.unicode.isprintable():
                    self.text = self._text[:self._cursor_pos] + event.unicode + self._text[self._cursor_pos:]
                    self._cursor_pos += 1

            self._cursor_visible = True
            self._cursor_timer = 0
            self.mark_render_dirty()
            return True

        return super().process_event(event, offset_x, offset_y)

    def update_animations(self, dt: float):
        super().update_animations(dt)
        if self._focused:
            self._cursor_timer += dt
            if self._cursor_timer >= 0.5:
                self._cursor_timer = 0
                self._cursor_visible = not self._cursor_visible
                self.mark_render_dirty()

    def draw(self, surface: pygame.Surface):
        # Draw background and border
        bg_color = parse_color(self.style.get("background_color", "#333333"))
        border_color = parse_color(self.style.get("border_color", "#666666" if not self._focused else "#0078d7"))
        border_width = self.style.get("border_width", 2)

        pygame.draw.rect(surface, bg_color, surface.get_rect())
        pygame.draw.rect(surface, border_color, surface.get_rect(), width=int(border_width))

        # Draw text
        font_name = self.style.get("font_name", None)
        font_size = self.style.get("font_size", 24)
        font = get_font(font_name, font_size)

        display_text = self._text
        text_color = parse_color(self.style.get("color", "#ffffff"))

        if not self._text and self._placeholder:
            display_text = self._placeholder
            text_color = parse_color(self.style.get("placeholder_color", "#888888"))

        text_surf = font.render(display_text, True, text_color)
        padding = 5
        surface.blit(text_surf, (padding, (self.layout_height - text_surf.get_height()) // 2))

        # Draw cursor
        if self._focused and self._cursor_visible:
            cursor_x = padding + font.size(self._text[:self._cursor_pos])[0]
            cursor_y = (self.layout_height - font.get_linesize()) // 2
            pygame.draw.line(surface, text_color, (cursor_x, cursor_y), (cursor_x, cursor_y + font.get_linesize()), 2)
