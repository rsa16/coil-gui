import pygame
from typing import Optional
from ..core.container import Container
from ..layout.flex import FlexLayout, FlexDirection, AlignItems
from ..utils.layout import set_default_size
from .label import Label

class Panel(Container):
    def __init__(self, title: str = "", **kwargs):
        layout = kwargs.pop("layout", FlexLayout(direction=FlexDirection.COLUMN))
        super().__init__(layout=layout, **kwargs)

        self.title_bar = Container(
            layout=FlexLayout(direction=FlexDirection.ROW, align=AlignItems.CENTER, padding=5),
            background_color="#444444",
            height=30
        )
        self.title_label = Label(title, font_size=18, color="#ffffff")
        self.title_bar.add_child(self.title_label)

        # Override add_child to add to a content area?
        # For simplicity, we just add title_bar as the first child
        # and subsequent children will be below it.
        super().add_child(self.title_bar)

        set_default_size(self, 200, 200)

    @property
    def title(self) -> str:
        return self.title_label.text

    @title.setter
    def title(self, value: str):
        self.title_label.text = value

    def draw(self, surface: pygame.Surface):
        # Draw background and border
        bg_color = self.style.get("background_color", "#222222")
        border_color = self.style.get("border_color", "#666666")

        pygame.draw.rect(surface, bg_color, surface.get_rect())
        pygame.draw.rect(surface, border_color, surface.get_rect(), width=1)
