import pygame
from typing import Optional, List
from .core.widget import Widget
from .style.theme import Theme
from .style.stylesheet import StyleSheet

class UIManager:
    def __init__(self, surface: pygame.Surface, theme: Optional[Theme] = None, stylesheet: Optional[StyleSheet] = None):
        self.target_surface = surface
        self.root: Optional[Widget] = None
        self.theme = theme or Theme()
        self.stylesheet = stylesheet or StyleSheet()
        self._dirty_rects: List[pygame.Rect] = []
        self._animations = []

    def set_root(self, widget: Widget):
        self.root = widget
        widget.manager = self

    def process_events(self, event: pygame.event.Event):
        if self.root:
            self.root.process_event(event)

    def update(self, dt: float):
        for anim in self._animations[:]:
            if hasattr(anim, 'step'):
                anim.step(dt)
            if getattr(anim, 'finished', False):
                self._animations.remove(anim)

        if self.root:
            self.root.recursive_update(dt)
            if self.root.is_layout_dirty():
                self.root.perform_layout()
                self.root.mark_render_dirty()

    def draw_ui(self) -> List[pygame.Rect]:
        self._dirty_rects.clear()
        if self.root:
            self.root.render(self.target_surface, self._dirty_rects, 0, 0)
        return self._dirty_rects

    def play_animation(self, animation):
        self._animations.append(animation)
