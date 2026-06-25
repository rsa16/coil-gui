import pygame
from typing import List, Tuple, Any
from ..core.container import Container
from ..layout.flex import FlexLayout, FlexDirection, AlignItems
from ..layout.absolute import AbsoluteLayout
from .label import Label
from .button import Button

class Tabs(Container):
    def __init__(self, tabs: List[Tuple[str, 'Widget']], **kwargs):
        layout = kwargs.pop("layout", FlexLayout(direction=FlexDirection.COLUMN))
        super().__init__(layout=layout, **kwargs)

        self._tabs_data = tabs
        self._current_index = 0

        # Header for tab buttons
        self.header = Container(
            layout=FlexLayout(direction=FlexDirection.ROW, gap=5, padding=5),
            background_color="#333333",
            height=40
        )
        self.add_child(self.header)

        # Content area
        self.content_area = Container(
            layout=AbsoluteLayout(),
            flex=1 # Take remaining space
        )
        self.add_child(self.content_area)

        self._rebuild_tabs()

    def _rebuild_tabs(self):
        self.header.children.clear()
        for i, (title, _) in enumerate(self._tabs_data):
            btn = Button(
                title,
                on_click=lambda idx=i: self.set_tab(idx),
                background_color="#444444" if i != self._current_index else "#0078d7",
                padding=5
            )
            self.header.add_child(btn)

        self.content_area.children.clear()
        if self._tabs_data:
            content = self._tabs_data[self._current_index][1]
            content.width = "100%" # Note: Need to check if "100%" is supported by layouts.
            # If not, we'll handle it in perform_layout.
            # Assuming for now we use layout constraints or manual sizing.
            self.content_area.add_child(content)

        self.mark_layout_dirty()

    def set_tab(self, index: int):
        if 0 <= index < len(self._tabs_data) and index != self._current_index:
            self._current_index = index
            self._rebuild_tabs()

    def perform_layout(self):
        super().perform_layout()
        # Ensure current content fills content area
        if self.content_area.children:
            content = self.content_area.children[0]
            content.set_layout_box(0, 0, self.content_area.layout_width, self.content_area.layout_height)
