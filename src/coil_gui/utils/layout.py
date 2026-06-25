"""
Utility functions for layout-related operations.

Provides helpers for resolving padding/margin tuples, setting default widget sizes,
and other common layout patterns.
"""

from typing import Tuple, Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.widget import Widget


def resolve_padding_tuple(
    padding: Union[float, Tuple[float, ...]]
) -> Tuple[float, float, float, float]:
    """
    Resolve a padding value into (top, bottom, left, right).

    Accepts:
    - A single float: uniform padding on all sides
    - A 2-tuple (vertical, horizontal): top/bottom and left/right
    - A 3-tuple (top, horizontal, bottom): top, left/right, bottom
    - A 4-tuple (top, right, bottom, left): all four sides individually

    Returns:
        Tuple[float, float, float, float]: (top, bottom, left, right)
    """
    if isinstance(padding, tuple):
        n = len(padding)
        if n == 1:
            return (float(padding[0]), float(padding[0]), float(padding[0]), float(padding[0]))
        elif n == 2:
            return (float(padding[0]), float(padding[0]), float(padding[1]), float(padding[1]))
        elif n == 3:
            return (float(padding[0]), float(padding[2]), float(padding[1]), float(padding[1]))
        elif n == 4:
            return (float(padding[0]), float(padding[2]), float(padding[3]), float(padding[1]))
        else:
            raise ValueError(f"Padding tuple must have 1-4 elements, got {n}")
    return (float(padding), float(padding), float(padding), float(padding))


def set_default_size(widget: "Widget", default_width: float, default_height: float):
    """
    Set default width/height on a widget if they are currently 0.

    This is used by widgets that need a minimum size when no explicit size is given.
    """
    if widget.width == 0:
        widget.width = default_width
    if widget.height == 0:
        widget.height = default_height


def apply_padding_to_widget(
    widget: "Widget",
    padding: Union[float, Tuple[float, ...]],
    padding_top: Optional[float] = None,
    padding_bottom: Optional[float] = None,
    padding_left: Optional[float] = None,
    padding_right: Optional[float] = None,
):
    """
    Apply padding values to a widget's per-side padding attributes.

    Handles both tuple padding and individual per-side overrides.
    """
    if isinstance(padding, tuple):
        pt, pb, pl, pr = resolve_padding_tuple(padding)
        widget.padding = 0.0
        widget.padding_top = pt
        widget.padding_bottom = pb
        widget.padding_left = pl
        widget.padding_right = pr
    else:
        widget.padding = float(padding)
        widget.padding_top = padding_top
        widget.padding_bottom = padding_bottom
        widget.padding_left = padding_left
        widget.padding_right = padding_right
