import pygame
from typing import Optional, Callable, Tuple
from ..core.container import Container
from ..core.widget import Widget
from ..layout.flex import FlexLayout, FlexDirection, JustifyContent, AlignItems
from ..layout.absolute import AbsoluteLayout
from ..utils.color import parse_color
from ..utils.layout import set_default_size
from .label import Label
from .button import Button
from .slider import Slider
from .text_input import TextInput


class ColorPicker(Container):
    def __init__(self, initial_color: str = "#ff0000", **kwargs):
        layout = kwargs.pop("layout", FlexLayout(direction=FlexDirection.COLUMN, padding=10))
        super().__init__(layout=layout, **kwargs)

        self._color = pygame.Color(initial_color)
        self.on_change: Optional[Callable[[str], None]] = kwargs.get("on_change")

        set_default_size(self, 300, 300)

        # Preview area
        self.preview = Widget(width=280, height=60)
        self.add_child(self.preview)

        # Sliders for R, G, B
        self.r_slider = Slider(value=self._color.r, min_val=0, max_val=255, on_change=lambda v: self._on_slider(0, v))
        self.g_slider = Slider(value=self._color.g, min_val=0, max_val=255, on_change=lambda v: self._on_slider(1, v))
        self.b_slider = Slider(value=self._color.b, min_val=0, max_val=255, on_change=lambda v: self._on_slider(2, v))

        row_r = Container(layout=FlexLayout(direction=FlexDirection.ROW, align=AlignItems.CENTER, gap=5))
        row_r.add_child(Label("R", width=20))
        row_r.add_child(self.r_slider)
        self.add_child(row_r)

        row_g = Container(layout=FlexLayout(direction=FlexDirection.ROW, align=AlignItems.CENTER, gap=5))
        row_g.add_child(Label("G", width=20))
        row_g.add_child(self.g_slider)
        self.add_child(row_g)

        row_b = Container(layout=FlexLayout(direction=FlexDirection.ROW, align=AlignItems.CENTER, gap=5))
        row_b.add_child(Label("B", width=20))
        row_b.add_child(self.b_slider)
        self.add_child(row_b)

        # Hex input
        hex_row = Container(layout=FlexLayout(direction=FlexDirection.ROW, align=AlignItems.CENTER, gap=5))
        hex_row.add_child(Label("#", width=15))
        self.hex_input = TextInput(text=self._to_hex(), width=80, on_submit=self._on_hex_submit)
        hex_row.add_child(self.hex_input)
        self.add_child(hex_row)

    def _to_hex(self) -> str:
        return f"{self._color.r:02x}{self._color.g:02x}{self._color.b:02x}"

    def _on_slider(self, channel: int, value: float):
        r, g, b = self._color.r, self._color.g, self._color.b
        if channel == 0:
            r = int(value)
        elif channel == 1:
            g = int(value)
        else:
            b = int(value)
        self._color = pygame.Color(r, g, b)
        self._update_ui()

    def _on_hex_submit(self, text: str):
        try:
            self._color = pygame.Color("#" + text)
            self._update_ui()
        except (ValueError, pygame.error):
            self.hex_input.text = self._to_hex()

    def _update_ui(self):
        self.r_slider.value = self._color.r
        self.g_slider.value = self._color.g
        self.b_slider.value = self._color.b
        self.hex_input.text = self._to_hex()
        self.preview.style.background_color = f"#{self._to_hex()}"
        self.mark_render_dirty()
        if self.on_change:
            self.on_change(f"#{self._to_hex()}")

    @property
    def color(self) -> str:
        return f"#{self._to_hex()}"

    @color.setter
    def color(self, value: str):
        try:
            self._color = pygame.Color(value)
            self._update_ui()
        except (ValueError, pygame.error):
            pass
