from .base import Layout
from .constraints import Size

class AbsoluteLayout(Layout):
    def measure(self, container, available_w: float, available_h: float) -> Size:
        max_w, max_h = 0.0, 0.0
        for child in container.children:
            res = child.measure(available_w, available_h)
            cx, cy = child.x, child.y
            max_w = max(max_w, cx + res.w)
            max_h = max(max_h, cy + res.h)
        return Size(w=max_w, h=max_h)

    def arrange(self, container, x: float, y: float, w: float, h: float):
        for child in container.children:
            cw = child.constraints.clamp_w(child.resolve_width(w))
            ch = child.constraints.clamp_h(child.resolve_height(h))
            child.set_layout_box(child.x, child.y, cw, ch)
