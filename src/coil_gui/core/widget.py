import pygame
from typing import Optional, List, Set, Any, TYPE_CHECKING, Tuple, Callable

from ..style.proxy import StyleProxy
from ..effects.base import Effect
from ..utils.color import parse_color
from ..binding.binder import bind

from ..layout.anchor import AnchorTargetProperty, Anchors
from ..layout.flex import FlexItem
from ..layout.constraints import Constraints, Size

from ..animation.controller import AnimationController
from ..animation.transition import TransitionManager

if TYPE_CHECKING:
    from ..manager import UIManager

class Widget:
    def __init__(self, x: float = 0, y: float = 0, width: float = 0, height: float = 0, **kwargs):
        self._x = x
        self._y = y
        self._width = width
        self._height = height

        # LayoutManager assigns the following values
        self.layout_x = x
        self.layout_y = y
        self.layout_width = width
        self.layout_height = height

        # Constraints
        self.min_width: float = kwargs.get("min_width", 0.0)
        self.max_width: float = kwargs.get("max_width", float("inf"))
        self.min_height: float = kwargs.get("min_height", 0.0)
        self.max_height: float = kwargs.get("max_height", float("inf"))

        # Padding (uniform or per-side)
        self.padding: float = kwargs.get("padding", 0.0)
        self.padding_top: Optional[float] = kwargs.get("padding_top", None)
        self.padding_bottom: Optional[float] = kwargs.get("padding_bottom", None)
        self.padding_left: Optional[float] = kwargs.get("padding_left", None)
        self.padding_right: Optional[float] = kwargs.get("padding_right", None)

        # Margin (uniform or per-side)
        self.margin: float = kwargs.get("margin", 0.0)
        self.margin_top: Optional[float] = kwargs.get("margin_top", None)
        self.margin_bottom: Optional[float] = kwargs.get("margin_bottom", None)
        self.margin_left: Optional[float] = kwargs.get("margin_left", None)
        self.margin_right: Optional[float] = kwargs.get("margin_right", None)

        # Z-Index
        self.z_index: int = kwargs.get("z_index", 0)

        self.opacity: float = 1.0
        self.rotation: float = 0.0
        self.scale: float = 1.0
        self.visible: bool = True
        self.origin: Tuple[float, float] = (0.0, 0.0)

        self.parent: Optional['Widget'] = None
        self.children: List['Widget'] = []
        self._manager: Optional['UIManager'] = None
        self._anchors: Optional['Anchors'] = None
        self._flex: Optional['FlexItem'] = None

        self.classes: Set[str] = set()
        if 'classes' in kwargs:
            cls = kwargs['classes']
            if isinstance(cls, str):
                self.classes.update(cls.split())
            else:
                self.classes.update(cls)

        self.id: str = kwargs.get('id', "")
        self.state_flags: Set[str] = set()

        self._layout_dirty: bool = True
        self._render_dirty: bool = True

        self._surface: Optional[pygame.Surface] = None
        self.clip_rect: Optional[pygame.Rect] = None
        self.render_offset = (0, 0)

        self._mounted: bool = False

        self.style = StyleProxy(self)
        self.effects: List[Effect] = []

        # Handle extra kwargs as style overrides
        for key, value in kwargs.items():
            if key not in ("id", "classes"):
                setattr(self.style, key, value)

        self.anim_controller = AnimationController(self)
        self._transition_manager = TransitionManager(self)
        self._bindings: List[Callable[[], None]] = []

    @property
    def x(self) -> float: return self._x

    @x.setter
    def x(self, value: float):
        if self._x != value:
            self._x = value
            self.mark_layout_dirty()

    @property
    def y(self) -> float:
        return self._y

    @y.setter
    def y(self, value: float):
        if self._y != value:
            self._y = value
            self.mark_layout_dirty()

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, value: float):
        if self._width != value:
            self._width = value
            self.mark_layout_dirty()

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, value: float):
        if self._height != value:
            self._height = value
            self.mark_layout_dirty()

    def set_layout_box(self, x: float, y: float, w: float, h: float):
        """Called by layout managers to set the final layout position and size."""
        if self.layout_x != x or self.layout_y != y or self.layout_width != w or self.layout_height != h:
            self.layout_x = x
            self.layout_y = y
            self.layout_width = w
            self.layout_height = h
            self.mark_render_dirty()
            self._layout_dirty = True

    def animate(
        self,
        property_name: str,
        end_value: Any,
        duration: float,
        easing: Any = "linear",
        delay: float = 0.0,
        on_complete: Optional[Callable[[], None]] = None,
        on_update: Optional[Callable[[Any], None]] = None,
    ):
        return self.anim_controller.animate(
            property_name, end_value, duration, easing, delay, on_complete, on_update
        )

    def measure(self, available_w: float, available_h: float) -> Any:
        """
        Measures the widget's preferred size given the available space.
        Returns a Size object.
        """
        w = self._width if self._width != 0 else 0
        h = self._height if self._height != 0 else 0
        return Size(w=self.constraints.clamp_w(w), h=self.constraints.clamp_h(h))

    def bind(self, property_name: str, observable: Any, transform: Optional[Callable[[Any], Any]] = None) -> Callable[[], None]:
        unbind_fn = bind(self, property_name, observable, transform)
        self._bindings.append(unbind_fn)
        return unbind_fn

    @property
    def constraints(self) -> Any:
        return Constraints(
            min_w=self.min_width,
            max_w=self.max_width,
            min_h=self.min_height,
            max_h=self.max_height
        )

    @property
    def anchors(self) -> 'Anchors':
        if self._anchors is None:
            self._anchors = Anchors(self)
        return self._anchors

    @property
    def flex(self) -> 'FlexItem':
        if self._flex is None:
            self._flex = FlexItem(self)
        return self._flex

    left = AnchorTargetProperty("left")
    right = AnchorTargetProperty("right")
    top = AnchorTargetProperty("top")
    bottom = AnchorTargetProperty("bottom")
    center_x = AnchorTargetProperty("center_x")
    center_y = AnchorTargetProperty("center_y")

    @property
    def manager(self) -> Optional['UIManager']:
        if self._manager:
            return self._manager
        if self.parent:
            return self.parent.manager
        return None

    @manager.setter
    def manager(self, value: 'UIManager'):
        was_mounted = self._mounted
        self._manager = value

        if value is not None and not was_mounted:
            self._mounted = True
            self.on_mount()
        elif value is None and was_mounted:
            self._mounted = False
            self.on_unmount()

        self.on_manager_changed()
        for child in self.children:
            child.manager = value

    def on_manager_changed(self):
        """Hook called when the manager is assigned or changed."""
        self.mark_layout_dirty()
        self.mark_render_dirty()

    def get_absolute_position(self) -> Tuple[float, float]:
        """Returns the absolute (x, y) coordinates of the widget on the screen."""
        ax, ay = self.x, self.y
        curr = self.parent
        while curr:
            ax += curr.x
            ay += curr.y
            curr = curr.parent
        return ax, ay

    def on_mount(self):
        """Called when the widget is added to a visible tree (has a manager)."""
        pass

    def on_unmount(self):
        """Called when the widget is removed from the tree."""
        pass

    def on_layout(self):
        """Called after layout is computed for this widget and its children."""
        pass

    def on_render_before(self, surface: pygame.Surface):
        """
        Called during rendering, before the widget's own content and children are drawn.
        Override this for custom drawing behind the widget.
        """
        pass

    def on_render_after(self, surface: pygame.Surface):
        """
        Called during rendering, after the widget's own content and children are drawn.
        Override this for custom drawing on top of the widget.
        """
        pass

    def add_child(self, child: 'Widget'):
        child.parent = self
        if self.manager:
            child.manager = self.manager
        self.children.append(child)
        self.mark_layout_dirty()
        self.mark_render_dirty()

    def remove_child(self, child: 'Widget'):
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            child.manager = None  # Use setter to trigger on_unmount
            self.mark_layout_dirty()
            self.mark_render_dirty()

    def mark_layout_dirty(self):
        self._layout_dirty = True
        if self.parent:
            self.parent.mark_layout_dirty()

    def mark_render_dirty(self):
        self._render_dirty = True
        if self.parent:
            self.parent.mark_render_dirty()

    def is_layout_dirty(self) -> bool:
        return self._layout_dirty

    def process_event(self, event: pygame.event.Event, offset_x: float = 0, offset_y: float = 0) -> bool:
        if not self.visible:
            return False

        abs_x = offset_x + self.layout_x
        abs_y = offset_y + self.layout_y

        # Calculate the actual top-left based on origin
        draw_x = abs_x - (self.origin[0] * self.layout_width)
        draw_y = abs_y - (self.origin[1] * self.layout_height)

        rect = pygame.Rect(draw_x, draw_y, self.layout_width, self.layout_height)

        consumed = False
        if event.type in (
            pygame.MOUSEMOTION,
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
        ):
            if rect.collidepoint(event.pos) and "disabled" not in self.state_flags:
                if "hover" not in self.state_flags:
                    self.state_flags.add("hover")
                    self.mark_render_dirty()
            else:
                if "hover" in self.state_flags:
                    self.state_flags.discard("hover")
                    self.mark_render_dirty()

        # Sort children by z_index descending for event processing (top-most first)
        sorted_children = sorted(self.children, key=lambda c: c.z_index, reverse=True)
        for child in sorted_children:
            if child.process_event(event, abs_x, abs_y):
                consumed = True
                break

        return consumed

    def perform_layout(self):
        self._layout_dirty = False
        for child in self.children:
            if child.is_layout_dirty():
                child.perform_layout()
        self.on_layout()

    def render(self, surface: pygame.Surface, dirty_rects: List[pygame.Rect], offset_x: float = 0, offset_y: float = 0):
        if not self.visible:
            return

        abs_x = offset_x + self.layout_x
        abs_y = offset_y + self.layout_y

        self.on_render_before(surface)

        if self._render_dirty or self._surface is None:
            w = max(1, int(self.layout_width))
            h = max(1, int(self.layout_height))
            content_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            self.draw(content_surf)

            final_surf = content_surf
            for effect in self.effects:
                final_surf = effect.process(final_surf, self)

            self._surface = final_surf
            self._render_dirty = False

        if self._surface:
            surf = self._surface
            if self.scale != 1.0 or self.rotation != 0.0:
                surf = pygame.transform.rotozoom(surf, self.rotation, self.scale)
            if self.opacity < 1.0:
                surf = surf.copy()
                surf.set_alpha(int(self.opacity * 255))

            # Offset by origin so (x, y) is the origin point
            rect = surf.get_rect()
            orig_center_x = abs_x + self.render_offset[0] + (0.5 - self.origin[0]) * self.layout_width
            orig_center_y = abs_y + self.render_offset[1] + (0.5 - self.origin[1]) * self.layout_height
            rect.center = (orig_center_x, orig_center_y)
            dest_rect = surface.blit(surf, rect)
            if dirty_rects is not None:
                dirty_rects.append(dest_rect)

        # Sort children by z_index ascending for rendering (bottom-most first)
        sorted_children = sorted(self.children, key=lambda c: c.z_index)
        for child in sorted_children:
            child.render(surface, dirty_rects, abs_x, abs_y)

        self.on_render_after(surface)

    def draw(self, surface: pygame.Surface):
        bg_color = self.style.get('background_color')
        if bg_color:
            surface.fill(parse_color(bg_color))

    def update_animations(self, dt: float):
        if self.anim_controller:
            self.anim_controller.update(dt)
        if self._transition_manager:
            self._transition_manager.update(dt)
        for child in self.children:
            child.update_animations(dt)

    def recursive_update(self, dt: float):
        self.update_animations(dt)
