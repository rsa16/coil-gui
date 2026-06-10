import pygame
from typing import Any
from .base import Effect
from ..utils.color import parse_color

class DropShadow(Effect):
    def __init__(self, offset=(0, 4), blur=8, spread=0, color=(0, 0, 0, 80)):
        self.offset = offset
        self.blur = blur
        self.spread = spread
        self.color = parse_color(color)

    def process(self, surface: pygame.Surface, widget: Any) -> pygame.Surface:
        w, h = surface.get_size()

        sigma = self.blur / 2.0
        blur_margin = int(sigma * 3)
        margin = (blur_margin + abs(self.spread)) * 2

        # original surface + margins + offset
        new_w = w + margin + abs(self.offset[0])
        new_h = h + margin + abs(self.offset[1])

        out = pygame.Surface((new_w, new_h), pygame.SRCALPHA)

        content_x = margin // 2 + max(0, -self.offset[0])
        content_y = margin // 2 + max(0, -self.offset[1])

        mask_w = w + self.spread * 2
        mask_h = h + self.spread * 2

        if mask_w <= 0 or mask_h <= 0:
            out.blit(surface, (content_x, content_y))
            return out

        mask_surf = pygame.Surface((mask_w + blur_margin * 2, mask_h + blur_margin * 2), pygame.SRCALPHA)

        if self.spread == 0:
            mask_surf.blit(surface, (blur_margin, blur_margin))
        else:
            scaled = pygame.transform.smoothscale(surface, (mask_w, mask_h))
            mask_surf.blit(scaled, (blur_margin, blur_margin))

        mask_surf.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)

        if self.blur > 0:
            radius = max(1, int(sigma))
            mask_surf = pygame.transform.gaussian_blur(mask_surf, radius)

        # centered on the content, then shifted by offset
        shadow_x = content_x + self.offset[0] - (mask_surf.get_width() - w) // 2
        shadow_y = content_y + self.offset[1] - (mask_surf.get_height() - h) // 2

        out.blit(mask_surf, (shadow_x, shadow_y))

        # blit original content on top of shadow
        out.blit(surface, (content_x, content_y))

        if hasattr(widget, 'render_offset'):
            widget.render_offset = (-content_x, -content_y)

        return out
