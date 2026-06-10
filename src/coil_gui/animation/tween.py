from typing import Any, Callable, Union, Optional, Tuple
from .easing import get_easing, EasingFunction
from ..utils.color import parse_color

def lerp(start: float, end: float, t: float) -> float:
    return start + (end - start) * t

def lerp_color(start_color: Tuple[int, int, int, int], end_color: Tuple[int, int, int, int], t: float) -> Tuple[int, int, int, int]:
    r = int(lerp(start_color[0], end_color[0], t))
    g = int(lerp(start_color[1], end_color[1], t))
    b = int(lerp(start_color[2], end_color[2], t))
    a = int(lerp(start_color[3], end_color[3], t))
    return (
        max(0, min(255, r)),
        max(0, min(255, g)),
        max(0, min(255, b)),
        max(0, min(255, a))
    )

def parse_to_rgba(val: Any) -> Optional[Tuple[int, int, int, int]]:
    if val is None:
        return None
    try:
        color = parse_color(val)
        if len(color) == 3:
            return (color[0], color[1], color[2], 255)
        elif len(color) == 4:
            return (color[0], color[1], color[2], color[3])
    except Exception:
        pass
    return None

class Tween:
    def __init__(
        self,
        target: Any,
        property_name: str,
        end_value: Any,
        duration: float,
        start_value: Any = None,
        easing: Union[str, EasingFunction] = "linear",
        delay: float = 0.0,
        on_complete: Optional[Callable[[], None]] = None,
        on_update: Optional[Callable[[Any], None]] = None,
    ):
        self.target = target
        self.property_name = property_name
        self.end_value = end_value
        self.duration = max(0.001, duration)
        self._start_value = start_value
        self.delay = delay
        self.on_complete = on_complete
        self.on_update = on_update

        if isinstance(easing, str):
            self.easing_fn = get_easing(easing)
        else:
            self.easing_fn = easing

        self.elapsed = 0.0
        self.started = False
        self.completed = False

        self._is_color = False
        self._resolved_start: Any = None
        self._resolved_end: Any = None

    def _resolve_values(self):
        # Get start value if not provided
        if self._start_value is None:
            parts = self.property_name.split(".")
            obj = self.target
            if isinstance(obj, dict):
                self._start_value = obj.get(parts[-1], 0.0)
            else:
                for part in parts[:-1]:
                    obj = getattr(obj, part)
                self._start_value = getattr(obj, parts[-1], 0.0)

        # Check if we are animating a color
        start_rgba = parse_to_rgba(self._start_value)
        end_rgba = parse_to_rgba(self.end_value)

        if start_rgba is not None and end_rgba is not None:
            self._is_color = True
            self._resolved_start = start_rgba
            self._resolved_end = end_rgba
        else:
            self._is_color = False
            self._resolved_start = self._start_value
            self._resolved_end = self.end_value

    def update(self, dt: float) -> bool:
        """
        Updates the tween. Returns True if completed.
        """
        if self.completed:
            return True

        if self.delay > 0.0:
            self.delay -= dt
            return False

        if not self.started:
            self._resolve_values()
            self.started = True

        self.elapsed += dt
        t = min(1.0, self.elapsed / self.duration)
        eased_t = self.easing_fn(t)

        # Interpolate
        if self._is_color:
            current_val = lerp_color(self._resolved_start, self._resolved_end, eased_t)
            # If original end_value was a hex string, convert back to hex
            if isinstance(self.end_value, str) and self.end_value.startswith("#"):
                current_val = f"#{current_val[0]:02x}{current_val[1]:02x}{current_val[2]:02x}"
        elif isinstance(self._resolved_start, (int, float)) and isinstance(self._resolved_end, (int, float)):
            current_val = lerp(self._resolved_start, self._resolved_end, eased_t)
            if isinstance(self._resolved_start, int) and isinstance(self._resolved_end, int):
                current_val = int(round(current_val))
        elif isinstance(self._resolved_start, tuple) and isinstance(self._resolved_end, tuple):
            current_val = tuple(
                lerp(s, e, eased_t) for s, e in zip(self._resolved_start, self._resolved_end)
            )
        else:
            # Fallback to end value at the end, start value before
            current_val = self._resolved_end if t >= 1.0 else self._resolved_start

        # Set property
        parts = self.property_name.split(".")
        obj = self.target
        if isinstance(obj, dict):
            obj[parts[-1]] = current_val
        else:
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], current_val)

        # Trigger update callback
        if self.on_update:
            self.on_update(current_val)

        # Check completion
        if t >= 1.0:
            self.completed = True
            if self.on_complete:
                self.on_complete()
            return True

        return False