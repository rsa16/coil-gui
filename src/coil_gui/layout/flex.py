from enum import Enum, auto
from typing import List, Optional, TYPE_CHECKING, Any, Tuple, Union
from .base import Layout
from .constraints import Size
from ..utils.layout import resolve_padding_tuple

if TYPE_CHECKING:
    from ..core.widget import Widget

class FlexDirection(Enum):
    """Defines the direction of the main axis in the flex layout."""
    ROW = "row"
    ROW_REVERSE = "row-reverse"
    COLUMN = "column"
    COLUMN_REVERSE = "column-reverse"

class JustifyContent(Enum):
    """Defines how space is distributed along the main axis."""
    START = "flex-start"
    CENTER = "center"
    END = "flex-end"
    SPACE_BETWEEN = "space-between"
    SPACE_AROUND = "space-around"
    SPACE_EVENLY = "space-evenly"

class AlignItems(Enum):
    """Defines the default alignment for items along the cross axis."""
    START = "flex-start"
    CENTER = "center"
    END = "flex-end"
    STRETCH = "stretch"

class AlignContent(Enum):
    """Defines how space is distributed along the cross axis when there are multiple lines."""
    START = "flex-start"
    CENTER = "center"
    END = "flex-end"
    STRETCH = "stretch"
    SPACE_BETWEEN = "space-between"
    SPACE_AROUND = "space-around"
    SPACE_EVENLY = "space-evenly"

class FlexWrap(Enum):
    """Defines whether the flex container is single-line or multi-line."""
    NOWRAP = "nowrap"
    WRAP = "wrap"
    WRAP_REVERSE = "wrap-reverse"

class FlexItem:
    """
    Represents the flex properties of an individual child widget.
    Allows per-child customization of grow, shrink, basis, and alignment.
    """
    def __init__(self, owner: 'Widget'):
        self._owner = owner
        self._grow: float = 0.0
        self._shrink: float = 1.0
        self._basis: Optional[float] = None
        self._align_self: Optional[AlignItems] = None

    def _dirty(self):
        """Marks the owner widget's layout as dirty to trigger a recalculation."""
        self._owner.mark_layout_dirty()

    @property
    def grow(self) -> float:
        """The flex grow factor, specifying how much of the remaining space should be assigned to this item."""
        return self._grow

    @grow.setter
    def grow(self, value: float):
        self._grow = value
        self._dirty()

    @property
    def shrink(self) -> float:
        """The flex shrink factor, specifying how much this item should shrink when space is insufficient."""
        return self._shrink

    @shrink.setter
    def shrink(self, value: float):
        self._shrink = value
        self._dirty()

    @property
    def basis(self) -> Optional[float]:
        """The initial main size of the flex item before free space is distributed."""
        return self._basis

    @basis.setter
    def basis(self, value: Optional[float]):
        self._basis = value
        self._dirty()

    @property
    def align_self(self) -> Optional[AlignItems]:
        """Allows the default cross-axis alignment to be overridden for this individual item."""
        return self._align_self

    @align_self.setter
    def align_self(self, value: Optional[AlignItems]):
        self._align_self = value
        self._dirty()

class FlexLayout(Layout):
    """
    CSS Flexbox Python implementation, more or less.
    Supports row/column flow, wrapping, alignment, gaps, padding, and per-child flex properties.

    Padding can be specified as:
    - A single float: uniform padding on all sides
    - A 2-tuple (vertical, horizontal): top/bottom and left/right
    - A 3-tuple (top, horizontal, bottom): top, left/right, bottom
    - A 4-tuple (top, right, bottom, left): all four sides individually
    """
    def __init__(self,
                 direction: Union[FlexDirection, str] = FlexDirection.ROW,
                 justify: Union[JustifyContent, str] = JustifyContent.START,
                 align: Union[AlignItems, str] = AlignItems.STRETCH,
                 wrap: Union[FlexWrap, str] = FlexWrap.NOWRAP,
                 align_content: Union[AlignContent, str] = AlignContent.STRETCH,
                 gap: float = 0.0,
                 row_gap: Optional[float] = None,
                 column_gap: Optional[float] = None,
                 padding: Union[float, Tuple[float, ...]] = 0.0,
                 padding_top: Optional[float] = None,
                 padding_bottom: Optional[float] = None,
                 padding_left: Optional[float] = None,
                 padding_right: Optional[float] = None):
        self.direction = FlexDirection(direction) if isinstance(direction, str) else direction
        self.justify = JustifyContent(justify) if isinstance(justify, str) else justify
        self.align = AlignItems(align) if isinstance(align, str) else align
        self.wrap = FlexWrap(wrap) if isinstance(wrap, str) else wrap
        self.align_content = AlignContent(align_content) if isinstance(align_content, str) else align_content
        self.gap = gap
        self.row_gap = row_gap
        self.column_gap = column_gap

        if isinstance(padding, tuple):
            pt, pb, pl, pr = resolve_padding_tuple(padding)
            self.padding = 0.0
            self.padding_top = pt
            self.padding_bottom = pb
            self.padding_left = pl
            self.padding_right = pr
        else:
            self.padding = padding
            self.padding_top = padding_top
            self.padding_bottom = padding_bottom
            self.padding_left = padding_left
            self.padding_right = padding_right

    def _get_padding(self) -> Tuple[float, float, float, float]:
        pt = self.padding_top if self.padding_top is not None else self.padding
        pb = self.padding_bottom if self.padding_bottom is not None else self.padding
        pl = self.padding_left if self.padding_left is not None else self.padding
        pr = self.padding_right if self.padding_right is not None else self.padding
        return pt, pb, pl, pr

    def _get_gaps(self) -> Tuple[float, float]:
        rg = self.row_gap if self.row_gap is not None else self.gap
        cg = self.column_gap if self.column_gap is not None else self.gap
        return rg, cg

    def _is_row_direction(self) -> bool:
        return self.direction in (FlexDirection.ROW, FlexDirection.ROW_REVERSE)

    def _get_main_and_cross_sizes(self, w: float, h: float) -> Tuple[float, float]:
        if self._is_row_direction():
            return w, h
        return h, w

    def _get_main_and_cross_gaps(self) -> Tuple[float, float]:
        rg, cg = self._get_gaps()
        if self._is_row_direction():
            return cg, rg
        return rg, cg

    def measure(self, container: 'Widget', available_w: float, available_h: float) -> Size:
        pt, pb, pl, pr = self._get_padding()
        # Ensure available space is at least 0
        available_w = max(0.0, available_w - (pl + pr))
        available_h = max(0.0, available_h - (pt + pb))

        lines = self._calculate_layout(container, available_w, available_h)

        max_main = 0.0
        total_cross = 0.0

        main_gap, cross_gap = self._get_main_and_cross_gaps()

        for i, line in enumerate(lines):
            line_main = sum(item[1] for item in line) + (main_gap * (len(line) - 1) if len(line) > 0 else 0)
            max_main = max(max_main, line_main)

            line_cross = max((item[2] for item in line), default=0.0)
            total_cross += line_cross
            if i > 0:
                total_cross += cross_gap

        if self._is_row_direction():
            return Size(w=max_main + pl + pr, h=total_cross + pt + pb)
        else:
            return Size(w=total_cross + pl + pr, h=max_main + pt + pb)

    def arrange(self, container: 'Widget', x: float, y: float, w: float, h: float):
        """
        Arranges and positions the children of the flex container based on flexbox rules.

        The arrangement process follows these steps:
        1. Subtracts the container's padding from the available width and height to find the content area.
        2. Calculates the layout lines by grouping items and resolving flexible lengths (grow/shrink).
        3. Distributes the lines along the cross axis based on the `align_content` property.
        4. Iterates through each line:
           a. Calculates the line's cross size, stretching it if `align_content` is set to STRETCH.
           b. Distributes the items along the main axis based on the `justify_content` property.
           c. Positions each item:
              i. Resolves the item's cross-axis alignment (`align-items` or `align-self`).
              ii. Adjusts coordinates for reverse directions (`row-reverse`, `column-reverse`, `wrap-reverse`).
              iii. Sets the child's final `x`, `y`, `width`, and `height` properties, taking into account the child's origin.
        """
        pt, pb, pl, pr = self._get_padding()
        w -= (pl + pr)
        h -= (pt + pb)

        lines = self._calculate_layout(container, w, h)
        main_gap, cross_gap = self._get_main_and_cross_gaps()
        is_row = self._is_row_direction()
        main_size, cross_size = self._get_main_and_cross_sizes(w, h)

        # 1. Distribute cross axis (align-content)
        cross_offset, cross_spacing, total_cross_size = self._distribute_cross_axis(lines, cross_size, cross_gap)
        curr_cross = cross_offset

        # 2. Position each line and its items
        for line in lines:
            line_cross_size = max((item[2] for item in line), default=0.0)
            if self.align_content == AlignContent.STRETCH and cross_size > total_cross_size and len(lines) > 0:
                line_cross_size += (cross_size - total_cross_size) / len(lines)

            # Distribute main axis (justify-content)
            main_offset, main_spacing = self._distribute_main_axis(line, main_size, main_gap)
            curr_main = main_offset

            for child, m_sz, c_sz in line:
                # Align items (cross axis)
                item_align = getattr(child.flex, "align_self", None) or self.align
                item_cross_offset, actual_c_sz = self._align_item_cross_axis(item_align, line_cross_size, c_sz)

                # Resolve final main and cross coordinates
                final_main = curr_main
                if self.direction in (FlexDirection.ROW_REVERSE, FlexDirection.COLUMN_REVERSE):
                    final_main = main_size - curr_main - m_sz

                final_cross = curr_cross
                if self.wrap == FlexWrap.WRAP_REVERSE:
                    final_cross = cross_size - curr_cross - line_cross_size

                if is_row:
                    final_x = final_main + pl + (child.origin[0] * m_sz)
                    final_y = final_cross + pt + item_cross_offset + (child.origin[1] * actual_c_sz)
                    child.set_layout_box(final_x, final_y, m_sz, actual_c_sz)
                else:
                    final_x = final_cross + pl + item_cross_offset + (child.origin[0] * actual_c_sz)
                    final_y = final_main + pt + (child.origin[1] * m_sz)
                    child.set_layout_box(final_x, final_y, actual_c_sz, m_sz)

                curr_main += m_sz + main_spacing

            curr_cross += line_cross_size + cross_spacing + (
                cross_gap if self.align_content not in (
                    AlignContent.SPACE_BETWEEN,
                    AlignContent.SPACE_AROUND,
                    AlignContent.SPACE_EVENLY,
                ) else 0
            )

    def _distribute_cross_axis(self, lines: List[List[Any]], cross_size: float, cross_gap: float) -> Tuple[float, float, float]:
        """Calculates the starting offset and spacing for lines along the cross axis."""
        total_cross_size = sum(max((item[2] for item in line), default=0.0) for line in lines)
        total_cross_size += cross_gap * (len(lines) - 1) if len(lines) > 1 else 0

        cross_offset = 0.0
        cross_spacing = 0.0
        extra_cross = cross_size - total_cross_size

        if self.align_content == AlignContent.CENTER:
            cross_offset = extra_cross / 2.0
        elif self.align_content == AlignContent.END:
            cross_offset = extra_cross
        elif self.align_content == AlignContent.SPACE_BETWEEN:
            if len(lines) > 1:
                cross_spacing = extra_cross / (len(lines) - 1)
        elif self.align_content == AlignContent.SPACE_AROUND:
            cross_spacing = extra_cross / len(lines)
            cross_offset = cross_spacing / 2.0
        elif self.align_content == AlignContent.SPACE_EVENLY:
            cross_spacing = extra_cross / (len(lines) + 1)
            cross_offset = cross_spacing

        return cross_offset, cross_spacing, total_cross_size

    def _distribute_main_axis(self, line: List[Tuple['Widget', float, float]], main_size: float, main_gap: float) -> Tuple[float, float]:
        """Calculates the starting offset and spacing for items along the main axis."""
        line_main_content_size = sum(item[1] for item in line)
        line_main_gap_size = main_gap * (len(line) - 1) if len(line) > 1 else 0
        line_total_main = line_main_content_size + line_main_gap_size

        extra_main = main_size - line_total_main
        main_offset = 0.0
        main_spacing = main_gap

        if self.justify == JustifyContent.CENTER:
            main_offset = extra_main / 2.0
        elif self.justify == JustifyContent.END:
            main_offset = extra_main
        elif self.justify == JustifyContent.SPACE_BETWEEN:
            if len(line) > 1:
                main_spacing = main_gap + (extra_main / (len(line) - 1))
        elif self.justify == JustifyContent.SPACE_AROUND:
            main_spacing = main_gap + (extra_main / len(line))
            main_offset = (main_spacing - main_gap) / 2.0
        elif self.justify == JustifyContent.SPACE_EVENLY:
            main_spacing = main_gap + (extra_main / (len(line) + 1))
            main_offset = main_spacing

        return main_offset, main_spacing

    def _align_item_cross_axis(self, item_align: AlignItems, line_cross_size: float, c_sz: float) -> Tuple[float, float]:
        """Calculates the cross-axis offset and size for an individual item based on alignment rules."""
        item_cross_offset = 0.0
        actual_c_sz = c_sz

        if item_align == AlignItems.CENTER:
            item_cross_offset = (line_cross_size - c_sz) / 2.0
        elif item_align == AlignItems.END:
            item_cross_offset = line_cross_size - c_sz
        elif item_align == AlignItems.STRETCH:
            actual_c_sz = line_cross_size

        return item_cross_offset, actual_c_sz

    def _calculate_layout(self, container: 'Widget', w: float, h: float) -> List[List[Tuple['Widget', float, float]]]:
        """
        Calculates the layout lines, grouping items and resolving flexible sizes.
        Returns a list of lines, where each line is a list of tuples: (child, main_size, cross_size).
        """
        w = max(0.0, w)
        h = max(0.0, h)
        is_row = self._is_row_direction()
        main_size, cross_size = self._get_main_and_cross_sizes(w, h)
        main_gap, _ = self._get_main_and_cross_gaps()

        # 1. Collect items and their preferred sizes
        items_data = self._collect_items_data(container, is_row, w, h)

        # 2. Group into lines
        lines = self._group_items_into_lines(items_data, main_size, main_gap)

        # 3. Resolve flexible lengths for each line
        return self._resolve_flexible_lengths(lines, main_size, main_gap, is_row)

    def _collect_items_data(self, container: 'Widget', is_row: bool, available_w: float, available_h: float) -> List[Dict[str, Any]]:
        """Collects child widgets and their initial preferred sizes, respecting constraints."""
        items_data = []
        for child in container.children:
            f = child.flex

            # If basis is not set, we measure the child to get its "natural" size
            if f.basis is not None:
                basis = f.basis
                if is_row:
                    basis = child.constraints.clamp_w(basis)
                    cross = child.constraints.clamp_h(child.resolve_height(available_h))
                else:
                    basis = child.constraints.clamp_h(basis)
                    cross = child.constraints.clamp_w(child.resolve_width(available_w))
            else:
                # Ask child to measure itself
                res = child.measure(available_w, available_h)
                if is_row:
                    basis = res.w
                    cross = res.h
                else:
                    basis = res.h
                    cross = res.w

            items_data.append({
                'child': child,
                'basis': basis,
                'cross': cross,
                'grow': f.grow,
                'shrink': f.shrink
            })
        return items_data

    def _group_items_into_lines(self, items_data: List[Dict[str, Any]], main_size: float, main_gap: float) -> List[List[Dict[str, Any]]]:
        """Groups flex items into lines based on wrapping rules and available main-axis space."""
        lines = []
        current_line = []
        current_line_main = 0.0

        for item in items_data:
            item_main = item['basis']
            gap = main_gap if len(current_line) > 0 else 0

            if self.wrap != FlexWrap.NOWRAP and current_line_main + gap + item_main > main_size and len(current_line) > 0:
                lines.append(current_line)
                current_line = []
                current_line_main = 0.0
                gap = 0

            current_line.append(item)
            current_line_main += gap + item_main

        if current_line:
            lines.append(current_line)

        return lines

    def _resolve_flexible_lengths(self, lines: List[List[Dict[str, Any]]], main_size: float, main_gap: float, is_row: bool) -> List[List[Tuple['Widget', float, float]]]:
        """Resolves flexible lengths (grow/shrink) for each line based on available free space."""
        resolved_lines = []
        for line in lines:
            line_main_basis = sum(item['basis'] for item in line)
            line_gap_total = main_gap * (len(line) - 1) if len(line) > 1 else 0
            free_space = main_size - (line_main_basis + line_gap_total)

            resolved_line = []
            if free_space > 0:
                total_grow = sum(item['grow'] for item in line)
                for item in line:
                    extra = (item['grow'] / total_grow) * free_space if total_grow > 0 else 0
                    val = item['basis'] + extra
                    val = item['child'].constraints.clamp_w(val) if is_row else item['child'].constraints.clamp_h(val)
                    resolved_line.append((item['child'], val, item['cross']))
            elif free_space < 0:
                total_shrink_factor = sum(item['basis'] * item['shrink'] for item in line)
                for item in line:
                    shrink_amount = (item['basis'] * item['shrink'] / total_shrink_factor) * abs(free_space) if total_shrink_factor > 0 else 0
                    val = item['basis'] - shrink_amount
                    val = item['child'].constraints.clamp_w(val) if is_row else item['child'].constraints.clamp_h(val)
                    resolved_line.append((item['child'], val, item['cross']))
            else:
                for item in line:
                    val = item['basis']
                    val = item['child'].constraints.clamp_w(val) if is_row else item['child'].constraints.clamp_h(val)
                    resolved_line.append((item['child'], val, item['cross']))
            resolved_lines.append(resolved_line)

        return resolved_lines
