import pygame
from typing import Optional, Callable, Any
from ..core.container import Container
from ..core.widget import Widget
from ..layout.flex import FlexLayout, FlexDirection, JustifyContent, AlignItems
from ..layout.absolute import AbsoluteLayout
from ..utils.color import parse_color
from .label import Label
from .button import Button


class Modal(Container):
    def __init__(self, title: str = "", content: Optional[Widget] = None, **kwargs):
        layout = kwargs.pop("layout", AbsoluteLayout())
        super().__init__(layout=layout, **kwargs)

        self._title = title
        self._content_widget = content
        self._open = False

        self.on_close: Optional[Callable[[], None]] = kwargs.get("on_close")

        # Overlay (semi-transparent background)
        self.overlay = Widget(visible=False, z_index=900)
        self.add_child(self.overlay)

        # Dialog box
        self.dialog = Container(
            layout=FlexLayout(direction=FlexDirection.COLUMN, padding=15),
            background_color="#2d2d2d",
            border_color="#555555",
            border_width=2,
            visible=False,
            z_index=901,
            width=400,
            height=300,
        )

        # Title bar
        title_bar = Container(
            layout=FlexLayout(direction=FlexDirection.ROW, justify=JustifyContent.SPACE_BETWEEN, align=AlignItems.CENTER),
            height=30,
        )
        self.title_label = Label(title, font_size=20, color="#ffffff")
        title_bar.add_child(self.title_label)
        close_btn = Button("X", on_click=self.close, width=30, height=30, background_color="#cc3333")
        title_bar.add_child(close_btn)
        self.dialog.add_child(title_bar)

        # Content area
        self.content_area = Container(
            layout=FlexLayout(direction=FlexDirection.COLUMN, padding=10),
            flex=1,
        )
        if content:
            self.content_area.add_child(content)
        self.dialog.add_child(self.content_area)

        self.add_child(self.dialog)

    def open(self):
        self._open = True
        self.overlay.visible = True
        self.dialog.visible = True
        self.mark_layout_dirty()

    def close(self):
        self._open = False
        self.overlay.visible = False
        self.dialog.visible = False
        self.mark_layout_dirty()
        if self.on_close:
            self.on_close()

    @property
    def is_open(self) -> bool:
        return self._open

    @property
    def content(self) -> Optional[Widget]:
        return self._content_widget

    @content.setter
    def content(self, widget: Widget):
        self._content_widget = widget
        self.content_area.children.clear()
        if widget:
            self.content_area.add_child(widget)
        self.mark_layout_dirty()

    def perform_layout(self):
        # Overlay fills the entire parent
        if self.parent:
            self.overlay.set_layout_box(0, 0, self.parent.layout_width, self.parent.layout_height)

        # Dialog is centered
        if self.parent:
            dw = self.dialog.width
            dh = self.dialog.height
            dx = (self.parent.layout_width - dw) / 2
            dy = (self.parent.layout_height - dh) / 2
            self.dialog.set_layout_box(dx, dy, dw, dh)
            self.dialog.perform_layout()

        super().perform_layout()

    def draw(self, surface: pygame.Surface):
        # Draw overlay background
        if self._open:
            overlay_color = parse_color("rgba(0, 0, 0, 0.5)")
            surface.fill(overlay_color)
