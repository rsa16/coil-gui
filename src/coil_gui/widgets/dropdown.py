import pygame
from typing import List, Any, Optional, Callable
from ..core.container import Container
from ..layout.flex import FlexLayout, FlexDirection, AlignItems, JustifyContent
from ..layout.absolute import AbsoluteLayout
from ..utils.layout import set_default_size
from ..utils.color import parse_color
from .label import Label
from .list_view import ListView


class Dropdown(Container):
    """A dropdown/select widget with a clickable button and expandable popup list."""

    def __init__(
        self,
        items: List[Any],
        selected_index: int = 0,
        *,
        on_change: Optional[Callable[[int, Any], None]] = None,
        **kwargs
    ):
        layout = kwargs.pop("layout", AbsoluteLayout())
        super().__init__(layout=layout, **kwargs)

        self._items = items
        self._selected_index = selected_index
        self._expanded = False
        self.on_change = on_change

        # ── Main button ──────────────────────────────────────────────
        self.main_button = Container(
            layout=FlexLayout(
                direction=FlexDirection.ROW,
                align=AlignItems.CENTER,
                justify=JustifyContent.SPACE_BETWEEN,
                padding=(0, 10, 0, 10),
            ),
            background_color="#161b22",
            border_color="#30363d",
            border_width=1,
            border_radius=6,
            height=34,
            width="100%",
        )

        self._label = Label(
            str(items[selected_index]) if items else "",
            font_size=14,
            color="#e6edf3",
        )
        self.main_button.add_child(self._label)

        # Arrow indicator
        self._arrow = Label("▼", font_size=10, color="#8b949e")
        self.main_button.add_child(self._arrow)

        self.add_child(self.main_button)

        # ── Popup list ───────────────────────────────────────────────
        self.popup = Container(
            layout=AbsoluteLayout(),
            background_color="#161b22",
            border_color="#30363d",
            border_width=1,
            border_radius=6,
            visible=False,
            z_index=100,
        )

        self.list_view = ListView(
            items=items,
            item_renderer=self._render_item,
            width="100%",
        )
        self.popup.add_child(self.list_view)
        self.add_child(self.popup)

        set_default_size(self, 180, 34)

    def _render_item(self, item: Any) -> Container:
        idx = self._items.index(item)
        is_selected = idx == self._selected_index

        btn = Container(
            layout=FlexLayout(
                direction=FlexDirection.ROW,
                align=AlignItems.CENTER,
                padding=(8, 12, 8, 12),
            ),
            background_color="#1c2333" if is_selected else "#161b22",
            width="100%",
            height=32,
        )

        lbl = Label(
            str(item),
            font_size=14,
            color="#58a6ff" if is_selected else "#e6edf3",
        )
        btn.add_child(lbl)

        btn._dropdown_index = idx
        return btn

    def toggle(self):
        self._expanded = not self._expanded
        self.popup.visible = self._expanded
        self._arrow.text = "▲" if self._expanded else "▼"
        self.mark_layout_dirty()

    def select(self, index: int):
        if index < 0 or index >= len(self._items):
            return
        self._selected_index = index
        self._label.text = str(self._items[index])
        self.toggle()
        if self.on_change:
            self.on_change(index, self._items[index])

    def process_event(self, event: pygame.event.Event, offset_x: float = 0, offset_y: float = 0) -> bool:
        if not self.visible:
            return False

        abs_x = offset_x + self.layout_x
        abs_y = offset_y + self.layout_y

        # Calculate the actual top-left based on origin
        draw_x = abs_x - (self.origin[0] * self.layout_width)
        draw_y = abs_y - (self.origin[1] * self.layout_height)

        # Main button rect
        btn_rect = pygame.Rect(draw_x, draw_y, self.layout_width, 34)

        # Popup rect (below button)
        popup_y = draw_y + 34 + 4
        popup_h = len(self._items) * 32 + 4
        popup_rect = pygame.Rect(draw_x, popup_y, self.layout_width, popup_h)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check popup items first (they're on top)
            if self._expanded and popup_rect.collidepoint(event.pos):
                rel_y = event.pos[1] - popup_y
                item_h = 32
                idx = int(rel_y // item_h)
                if 0 <= idx < len(self._items):
                    self.select(idx)
                return True

            # Check main button click
            if btn_rect.collidepoint(event.pos):
                self.toggle()
                return True

            # Click outside popup closes it
            if self._expanded:
                self._expanded = False
                self.popup.visible = False
                self._arrow.text = "▼"
                self.mark_layout_dirty()
                return True

        return super().process_event(event, offset_x, offset_y)

    def perform_layout(self):
        # Main button fills the top
        self.main_button.set_layout_box(0, 0, self.layout_width, 34)
        self.main_button.perform_layout()

        # Popup is below main button with a small gap
        if self._expanded:
            popup_h = len(self._items) * 32 + 4
            self.popup.set_layout_box(0, 34 + 4, self.layout_width, popup_h)
            self.popup.perform_layout()

        super().perform_layout()

    def draw(self, surface: pygame.Surface):
        # Draw background for the dropdown itself
        super().draw(surface)

        # Draw popup border if visible
        if self._expanded and self.popup.visible:
            popup_rect = surface.get_rect()
            border_color = parse_color("#30363d")
            pygame.draw.rect(surface, border_color, popup_rect, width=1, border_radius=6)
