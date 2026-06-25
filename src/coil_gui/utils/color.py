import pygame
import re
import colorsys
from typing import Union, Tuple, List
from typing_extensions import TypeAlias

ColorType: TypeAlias = Union[
    str, Tuple[int, int, int], Tuple[int, int, int, int], pygame.Color, List[int]
]


def parse_color(color: ColorType) -> pygame.Color:
    """Parse a color from string, tuple, or list into a pygame.Color."""
    if isinstance(color, pygame.Color):
        return color
    if isinstance(color, str):
        color = color.strip().lower()
        if color == "transparent":
            return pygame.Color(0, 0, 0, 0)
        try:
            return pygame.Color(color)
        except (ValueError, pygame.error):
            pass

        # rgb/rgba
        rgb_match = re.match(
            r"rgba?\(\s*(\d+%?)\s*,\s*(\d+%?)\s*,\s*(\d+%?)\s*(?:,\s*(\d*(?:\.\d+)?%?)\s*)?\)",
            color,
        )
        if rgb_match:
            r_s, g_s, b_s, a_s = rgb_match.groups()

            def _v(s, m):
                return int(float(s[:-1]) / 100.0 * m) if s.endswith("%") else int(s)

            r = _v(r_s, 255)
            g = _v(g_s, 255)
            b = _v(b_s, 255)
            a = 255
            if a_s is not None:
                a = int(float(a_s[:-1]) / 100.0 * 255) if a_s.endswith("%") else int(float(a_s) * 255)
            return pygame.Color(r, g, b, max(0, min(255, a)))

        # hsl/hsla
        hsl_match = re.match(
            r"hsla?\(\s*(\d*(?:\.\d+)?)\s*,\s*(\d*(?:\.\d+)?)%\s*,\s*(\d*(?:\.\d+)?)%\s*(?:,\s*(\d*(?:\.\d+)?%?)\s*)?\)",
            color,
        )
        if hsl_match:
            h_s, s_s, l_s, a_s = hsl_match.groups()
            h = float(h_s) / 360.0
            s = float(s_s) / 100.0
            l = float(l_s) / 100.0
            r_f, g_f, b_f = colorsys.hls_to_rgb(h, l, s)
            a = 255
            if a_s is not None:
                a = int(float(a_s[:-1]) / 100.0 * 255) if a_s.endswith("%") else int(float(a_s) * 255)
            return pygame.Color(
                int(r_f * 255), int(g_f * 255), int(b_f * 255), max(0, min(255, a))
            )

    if isinstance(color, (tuple, list)):
        if len(color) == 3:
            return pygame.Color(color[0], color[1], color[2], 255)
        elif len(color) == 4:
            return pygame.Color(color[0], color[1], color[2], color[3])
    raise ValueError(f"Invalid color format: {color}")
