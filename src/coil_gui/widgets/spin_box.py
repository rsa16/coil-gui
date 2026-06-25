import pygame
from typing import Optional, Callable
from ..core.container import Container
from ..layout.flex import FlexLayout, FlexDirection, AlignItems
from .label import Label
from .button import Button
from .text_input import TextInput

class SpinBox(Container):
    def __init__(self, value: float = 0, min_val: float = -float('inf'), max_val: float = float('inf'), step: float = 1, **kwargs):
        layout = kwargs.pop("layout", FlexLayout(direction=FlexDirection.ROW, align=AlignItems.CENTER))
        super().__init__(layout=layout, **kwargs)

        self._value = value
        self._min_val = min_val
        self._max_val = max_val
        self._step = step

        self.on_change: Optional[Callable[[float], None]] = kwargs.get("on_change")

        self.input = TextInput(text=str(value), width=60)
        self.input.on_submit = self._on_input_submit
        self.add_child(self.input)

        self.btn_container = Container(layout=FlexLayout(direction=FlexDirection.COLUMN))
        self.add_child(self.btn_container)

        self.btn_up = Button("+", on_click=self.increment, width=30, height=20, padding=2)
        self.btn_down = Button("-", on_click=self.decrement, width=30, height=20, padding=2)
        self.btn_container.add_child(self.btn_up)
        self.btn_container.add_child(self.btn_down)

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, val: float):
        val = max(self._min_val, min(self._max_val, val))
        if self._value != val:
            self._value = val
            self.input.text = str(val)
            if self.on_change:
                self.on_change(val)
            self.mark_render_dirty()

    def increment(self):
        self.value += self._step

    def decrement(self):
        self.value -= self._step

    def _on_input_submit(self, text: str):
        try:
            val = float(text)
            self.value = val
        except ValueError:
            self.input.text = str(self._value)
