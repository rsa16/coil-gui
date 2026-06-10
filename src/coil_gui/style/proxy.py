from typing import Any, Dict, Optional, TYPE_CHECKING
from .theme import Theme

if TYPE_CHECKING:
    from .stylesheet import StyleSheet

class StyleProxy:
    """
    A proxy object that manages styling for a specific widget.

    It handles computed styles from stylesheets, inline style overrides,
    transition styles, and theme variable resolution.
    """

    def __init__(self, widget):
        self._widget = widget
        self._inline_styles: Dict[str, Any] = {}
        self._computed_cache: Dict[str, Any] = {}
        self._last_stylesheet_id: int = -1
        self._last_state_hash: int = -1
        self._transition_styles: Dict[str, Any] = {}

    @property
    def theme(self) -> Theme:
        """Returns the current theme from the UI manager, or a default Theme."""
        if self._widget.manager:
            return self._widget.manager.theme
        return Theme()

    @property
    def stylesheet(self) -> Optional["StyleSheet"]:
        """Returns the current stylesheet from the UI manager, if available."""
        if self._widget.manager:
            return self._widget.manager.stylesheet
        return None

    def _ensure_computed(self):
        """
        Ensures that the computed styles are up-to-date based on the
        current stylesheet and widget state.
        """
        ss = self.stylesheet
        state_hash = hash(frozenset(getattr(self._widget, "state_flags", set())))
        if ss:
            current_id = id(ss) + ss._update_counter
            if (
                current_id != self._last_stylesheet_id
                or state_hash != self._last_state_hash
            ):
                old_style = dict(self._computed_cache)
                new_style = ss.compute_style(self._widget)
                self._computed_cache = new_style
                self._last_stylesheet_id = current_id
                self._last_state_hash = state_hash

                if hasattr(self._widget, "_transition_manager") and self._widget._transition_manager:
                    self._widget._transition_manager.handle_style_change(old_style, new_style)
        else:
            self._computed_cache = {}
            self._last_stylesheet_id = -1

    def get(self, name: str, default: Any = None) -> Any:
        """
        Retrieves a style property by name.

        Resolution order:
        1. Transition styles (active animations)
        2. Inline styles (overrides set directly on the proxy)
        3. Computed styles (from stylesheets, with theme variable resolution)
        4. Default value
        """
        self._ensure_computed()

        if name in self._transition_styles:
            return self._transition_styles[name]

        if name in self._inline_styles:
            return self._inline_styles[name]

        if name in self._computed_cache:
            val = self._computed_cache[name]
            if isinstance(val, str) and val.startswith("$"):
                return self.theme.get_var(val[1:])
            return val
        return default

    def __getattr__(self, name: str) -> Any:
        # avoid recursion for internal names
        if name.startswith("_"):
            raise AttributeError(f"'StyleProxy' object has no attribute '{name}'")

        val = self.get(name)
        if val is None:
            return None
        return val

    def __setattr__(self, name: str, value: Any):
        if name in (
            "_widget",
            "_inline_styles",
            "_computed_cache",
            "_last_stylesheet_id",
            "_last_state_hash",
            "_transition_styles",
        ):
            super().__setattr__(name, value)
        else:
            self._inline_styles[name] = value
            if hasattr(self._widget, "mark_render_dirty"):
                self._widget.mark_render_dirty()
            if name in ("padding", "margin", "width", "height", "flex", "gap") and hasattr(self._widget, "mark_layout_dirty"):
                self._widget.mark_layout_dirty()
