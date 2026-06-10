def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between a minimum and maximum."""
    return max(min_val, min(value, max_val))

def lerp(start: float, end: float, t: float) -> float:
    """Linearly interpolate between start and end by t."""
    return start + (end - start) * t
