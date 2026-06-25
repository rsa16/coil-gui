import pygame
import re
from typing import List, Tuple, Optional, Any
from ..core.widget import Widget
from ..utils.fonts import get_font
from ..utils.color import parse_color

class RichLabel(Widget):
    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs)
        self._text = text
        self._tokens: List[Tuple[str, dict]] = []
        self._parse_text()
        self._update_size()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        if self._text != value:
            self._text = value
            self._parse_text()
            self._update_size()
            self.mark_render_dirty()
            self.mark_layout_dirty()

    def _parse_text(self):
        # Extremely simple parser for [b], [i], [color=#hex]
        # Format: [tag]text[/tag] or [tag=val]text[/tag]

        self._tokens = []
        pattern = r"\[(/?[a-z]+(?:=[^\]]*)?)\]"

        last_pos = 0
        current_style = {
            "bold": False,
            "italic": False,
            "color": None
        }

        style_stack = []

        for match in re.finditer(pattern, self._text):
            # Text before the tag
            if match.start() > last_pos:
                text_part = self._text[last_pos:match.start()]
                self._tokens.append((text_part, current_style.copy()))

            tag_content = match.group(1)
            if tag_content.startswith("/"):
                # Closing tag
                if style_stack:
                    current_style = style_stack.pop()
            else:
                # Opening tag
                style_stack.append(current_style.copy())
                if tag_content == "b":
                    current_style["bold"] = True
                elif tag_content == "i":
                    current_style["italic"] = True
                elif tag_content.startswith("color="):
                    current_style["color"] = tag_content.split("=")[1]

            last_pos = match.end()

        if last_pos < len(self._text):
            self._tokens.append((self._text[last_pos:], current_style.copy()))

    def _get_font_for_token(self, style: dict) -> pygame.font.Font:
        font_name = self.style.get('font_name', None)
        font_size = self.style.get('font_size', 24)

        # This is a bit tricky since get_font doesn't currently support bold/italic flags
        # if they are not in the font name itself.
        # For simplicity, we'll just use the base font for now, or assume name might contain bold/italic
        # In a real engine, we'd have a better font manager.

        font = get_font(font_name, font_size)
        font.set_bold(style["bold"])
        font.set_italic(style["italic"])
        return font

    def _update_size(self):
        total_w = 0
        max_h = 0

        for text, style in self._tokens:
            font = self._get_font_for_token(style)
            w, h = font.size(text)
            total_w += w
            max_h = max(max_h, h)

        self.width = total_w
        self.height = max_h

    def measure(self, available_w: float, available_h: float) -> Any:
        from ..layout.constraints import Size
        self._update_size()
        return Size(w=self.constraints.clamp_w(self.width), h=self.constraints.clamp_h(self.height))

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

        default_color_val = self.style.get('color', '#ffffff')

        curr_x = 0
        for text, style in self._tokens:
            font = self._get_font_for_token(style)
            color_val = style["color"] or default_color_val
            color = parse_color(color_val)

            text_surf = font.render(text, True, color)
            surface.blit(text_surf, (curr_x, 0))
            curr_x += text_surf.get_width()
