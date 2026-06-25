from typing import Any, Optional
from .widget import Widget
from ..layout.base import Layout
from ..layout.absolute import AbsoluteLayout
from ..layout.constraints import Size

class Container(Widget):
    def __init__(self, layout: Optional[Layout] = None, **kwargs):
        super().__init__(**kwargs)
        self.layout: Layout = layout or AbsoluteLayout()

    def measure(self, available_w: float, available_h: float) -> Any:
        w = self.width
        h = self.height

        # If either is 0 (or not set), we measure children
        if w == 0 or h == 0:
            measured_size = self.layout.measure(self, available_w, available_h)
            if w == 0:
                w = measured_size.w
            if h == 0:
                h = measured_size.h

        return Size(w=self.constraints.clamp_w(w), h=self.constraints.clamp_h(h))

    def perform_layout(self):
        # If sizes are not set, we should measure ourselves first to expand if needed
        # We use layout_width/height if assigned by parent, otherwise fallback to requested width/height
        w = self.layout_width if self.layout_width != 0 else self.width
        h = self.layout_height if self.layout_height != 0 else self.height

        if w == 0 or h == 0:
            new_size = self.measure(float('inf'), float('inf'))
            if w == 0:
                w = new_size.w
            if h == 0:
                h = new_size.h

        # Update layout box if we just auto-sized
        if self.layout_width == 0:
            self.layout_width = w
        if self.layout_height == 0:
            self.layout_height = h

        for child in self.children:
            resolved_w = child.resolve_width(self.layout_width)
            resolved_h = child.resolve_height(self.layout_height)
            if resolved_w != 0:
                child.layout_width = resolved_w
            if resolved_h != 0:
                child.layout_height = resolved_h

        # Arrange children
        self.layout.arrange(self, 0, 0, w, h)

        super().perform_layout()
