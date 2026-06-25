import pygame
from typing import Optional, Any
from ..core.container import Container
from ..layout.absolute import AbsoluteLayout
from ..layout.constraints import Size
from ..utils.layout import set_default_size

class ScrollView(Container):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._scroll_x = 0.0
        self._scroll_y = 0.0
        self._show_scrollbar_v = True
        self._show_scrollbar_h = False

        set_default_size(self, 200, 200)

    @property
    def scroll_y(self) -> float:
        return self._scroll_y

    @scroll_y.setter
    def scroll_y(self, value: float):
        content_height = self._get_content_height()
        max_scroll = max(0, content_height - self.layout_height)
        self._scroll_y = max(0, min(max_scroll, value))
        self.mark_render_dirty()

    def _get_content_height(self) -> float:
        if not self.children:
            return 0
        return max(child.layout_y + child.layout_height for child in self.children)

    def process_event(self, event: pygame.event.Event, offset_x: float = 0, offset_y: float = 0) -> bool:
        if not self.visible:
            return False

        abs_x = offset_x + self.layout_x
        abs_y = offset_y + self.layout_y
        rect = pygame.Rect(abs_x, abs_y, self.layout_width, self.layout_height)

        if event.type == pygame.MOUSEWHEEL:
            if rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_y -= event.y * 30
                return True

        # When passing events to children, we need to account for scroll
        # However, Widget.process_event uses layout_x/y which are relative to parent.
        # We need to override process_event to apply scroll offset to children.

        # Sort children by z_index descending for event processing (top-most first)
        sorted_children = sorted(self.children, key=lambda c: c.z_index, reverse=True)
        for child in sorted_children:
            if child.process_event(event, abs_x - self._scroll_x, abs_y - self._scroll_y):
                return True

        return False

    def render(self, surface: pygame.Surface, dirty_rects: List[pygame.Rect], offset_x: float = 0, offset_y: float = 0):
        if not self.visible:
            return

        abs_x = offset_x + self.layout_x
        abs_y = offset_y + self.layout_y

        # Draw background
        self.on_render_before(surface)

        # Create a clipped surface for children
        w = max(1, int(self.layout_width))
        h = max(1, int(self.layout_height))

        # If we are dirty, we might need to redraw our own background
        if self._render_dirty or self._surface is None:
            self._surface = pygame.Surface((w, h), pygame.SRCALPHA)
            self.draw(self._surface)
            self._render_dirty = False

        surface.blit(self._surface, (abs_x, abs_y))
        if dirty_rects is not None:
            dirty_rects.append(pygame.Rect(abs_x, abs_y, w, h))

        # Render children onto a sub-surface or use clipping
        # Using a sub-surface is easier for scrolling
        content_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # We don't want to use child.render's normal offset because we are clipping
        # Actually, let's just use surface.set_clip

        old_clip = surface.get_clip()
        surface.set_clip(pygame.Rect(abs_x, abs_y, w, h))

        for child in sorted(self.children, key=lambda c: c.z_index):
            child.render(surface, dirty_rects, abs_x - self._scroll_x, abs_y - self._scroll_y)

        surface.set_clip(old_clip)

        # Draw scrollbars
        if self._show_scrollbar_v:
            content_h = self._get_content_height()
            if content_h > self.layout_height:
                sb_width = 8
                sb_height = max(20, (self.layout_height / content_h) * self.layout_height)
                sb_y = (self._scroll_y / content_h) * self.layout_height
                pygame.draw.rect(surface, (100, 100, 100, 150), (abs_x + self.layout_width - sb_width, abs_y + sb_y, sb_width, sb_height))

        self.on_render_after(surface)
