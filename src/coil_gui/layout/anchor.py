from typing import Optional, Union, TYPE_CHECKING, Any
from .base import Layout
from .constraints import Size

if TYPE_CHECKING:
    from ..core.widget import Widget

class AnchorTarget:
    def __init__(self, widget: 'Widget', edge: str):
        self.widget = widget
        self.edge = edge

class AnchorProperty:
    def __init__(self, default: Any = None):
        self.default = default
        self.name = ""

    def __set_name__(self, owner, name):
        self.name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return getattr(obj, self.name, self.default)

    def __set__(self, obj, value):
        setattr(obj, self.name, value)
        obj._dirty()

class AnchorTargetProperty:
    def __init__(self, edge: str):
        self.edge = edge

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return AnchorTarget(obj, self.edge)

class Anchors:
    left = AnchorProperty()
    right = AnchorProperty()
    top = AnchorProperty()
    bottom = AnchorProperty()
    center_x = AnchorProperty()
    center_y = AnchorProperty()

    margins = AnchorProperty(0.0)
    left_margin = AnchorProperty()
    right_margin = AnchorProperty()
    top_margin = AnchorProperty()
    bottom_margin = AnchorProperty()

    def __init__(self, owner: 'Widget'):
        self._owner = owner

    def _dirty(self):
        self._owner.mark_layout_dirty()

    def fill(self, target: 'Widget'):
        self.left = AnchorTarget(target, "left")
        self.right = AnchorTarget(target, "right")
        self.top = AnchorTarget(target, "top")
        self.bottom = AnchorTarget(target, "bottom")

    def center_in(self, target: 'Widget'):
        self.center_x = AnchorTarget(target, "center_x")
        self.center_y = AnchorTarget(target, "center_y")

class AnchorLayout(Layout):
    def measure(self, container: 'Widget', available_w: float, available_h: float) -> Size:
        return Size(w=available_w, h=available_h)

    def arrange(self, container: 'Widget', x: float, y: float, w: float, h: float):
        for child in container.children:
            self._resolve_child(child, container, w, h)

    def _resolve_child(self, child: 'Widget', container: 'Widget', cw: float, ch: float):
        a = child.anchors

        # Determine margins
        m_left = a.left_margin if a.left_margin is not None else a.margins
        m_right = a.right_margin if a.right_margin is not None else a.margins
        m_top = a.top_margin if a.top_margin is not None else a.margins
        m_bottom = a.bottom_margin if a.bottom_margin is not None else a.margins

        # Get child preferred size
        res = child.measure(cw, ch)

        # Horizontal resolution
        final_x = child.layout_x
        final_w = res.w

        left_val = self._get_anchor_val(a.left, child, container, "horizontal", cw, ch)
        right_val = self._get_anchor_val(a.right, child, container, "horizontal", cw, ch)
        center_x_val = self._get_anchor_val(a.center_x, child, container, "horizontal", cw, ch)

        if left_val is not None and right_val is not None:
            # Stretch between left and right
            final_x = left_val + m_left
            final_w = (right_val - m_right) - final_x
        elif left_val is not None:
            # Shifted by origin
            final_x = left_val + m_left + (child.origin[0] * res.w)
        elif right_val is not None:
            final_x = right_val - m_right - ((1.0 - child.origin[0]) * res.w)
        elif center_x_val is not None:
            final_x = center_x_val + (child.origin[0] - 0.5) * res.w

        # Vertical resolution
        final_y = child.layout_y
        final_h = res.h

        top_val = self._get_anchor_val(a.top, child, container, "vertical", cw, ch)
        bottom_val = self._get_anchor_val(a.bottom, child, container, "vertical", cw, ch)
        center_y_val = self._get_anchor_val(a.center_y, child, container, "vertical", cw, ch)

        if top_val is not None and bottom_val is not None:
            final_y = top_val + m_top
            final_h = (bottom_val - m_bottom) - final_y
        elif top_val is not None:
            final_y = top_val + m_top + (child.origin[1] * res.h)
        elif bottom_val is not None:
            final_y = bottom_val - m_bottom - ((1.0 - child.origin[1]) * res.h)
        elif center_y_val is not None:
            final_y = center_y_val + (child.origin[1] - 0.5) * res.h

        # Apply results. (x, y) represent the origin point.
        child.set_layout_box(final_x, final_y, max(0, final_w), max(0, final_h))

    def _get_anchor_val(self, target: Optional[AnchorTarget], child: 'Widget', container: 'Widget', axis: str, cw: float, ch: float) -> Optional[float]:
        if target is None:
            return None

        t_w = target.widget
        # Coordinate system is relative to container
        is_parent = (t_w == container or t_w == child.parent)

        if axis == "horizontal":
            base = 0 if is_parent else t_w.layout_x
            tw = cw if is_parent else t_w.layout_width
            # If target is sibling, they are relative to same origin, so use their bounds
            if not is_parent:
                 # Adjust base to top-left of sibling (x is already origin point)
                 base = t_w.layout_x - (t_w.origin[0] * t_w.layout_width)

            if target.edge == "left": return base
            if target.edge == "right": return base + tw
            if target.edge == "center_x": return base + tw / 2.0
        else:
            base = 0 if is_parent else t_w.layout_y
            th = ch if is_parent else t_w.layout_height
            if not is_parent:
                 base = t_w.layout_y - (t_w.origin[1] * t_w.layout_height)

            if target.edge == "top": return base
            if target.edge == "bottom": return base + th
            if target.edge == "center_y": return base + th / 2.0

        return None
