import math
from typing import Callable

EasingFunction = Callable[[float], float]

def linear(t: float) -> float:
    return t

def quad_in(t: float) -> float:
    return t * t

def quad_out(t: float) -> float:
    return t * (2.0 - t)

def quad_in_out(t: float) -> float:
    if t < 0.5:
        return 2.0 * t * t
    return -1.0 + (4.0 - 2.0 * t) * t

def cubic_in(t: float) -> float:
    return t * t * t

def cubic_out(t: float) -> float:
    t -= 1.0
    return t * t * t + 1.0

def cubic_in_out(t: float) -> float:
    if t < 0.5:
        return 4.0 * t * t * t
    t -= 1.0
    return 4.0 * t * t * t + 1.0

def quart_in(t: float) -> float:
    return t * t * t * t

def quart_out(t: float) -> float:
    t -= 1.0
    return 1.0 - t * t * t * t

def quart_in_out(t: float) -> float:
    if t < 0.5:
        return 8.0 * t * t * t * t
    t -= 1.0
    return 1.0 - 8.0 * t * t * t * t

def quint_in(t: float) -> float:
    return t * t * t * t * t

def quint_out(t: float) -> float:
    t -= 1.0
    return t * t * t * t * t + 1.0

def quint_in_out(t: float) -> float:
    if t < 0.5:
        return 16.0 * t * t * t * t * t
    t -= 1.0
    return 16.0 * t * t * t * t * t + 1.0

def sine_in(t: float) -> float:
    return 1.0 - math.cos(t * math.pi / 2.0)

def sine_out(t: float) -> float:
    return math.sin(t * math.pi / 2.0)

def sine_in_out(t: float) -> float:
    return 0.5 * (1.0 - math.cos(t * math.pi))

def expo_in(t: float) -> float:
    return 0.0 if t == 0.0 else math.pow(2.0, 10.0 * (t - 1.0))

def expo_out(t: float) -> float:
    return 1.0 if t == 1.0 else 1.0 - math.pow(2.0, -10.0 * t)

def expo_in_out(t: float) -> float:
    if t == 0.0:
        return 0.0
    if t == 1.0:
        return 1.0
    if t < 0.5:
        return 0.5 * math.pow(2.0, 10.0 * (2.0 * t - 1.0))
    return 0.5 * (2.0 - math.pow(2.0, -10.0 * (2.0 * t - 1.0)))

def circ_in(t: float) -> float:
    return 1.0 - math.sqrt(1.0 - t * t)

def circ_out(t: float) -> float:
    t -= 1.0
    return math.sqrt(1.0 - t * t)

def circ_in_out(t: float) -> float:
    if t < 0.5:
        return 0.5 * (1.0 - math.sqrt(1.0 - 4.0 * t * t))
    t = 2.0 * t - 2.0
    return 0.5 * (math.sqrt(1.0 - t * t) + 1.0)

def back_in(t: float, s: float = 1.70158) -> float:
    return t * t * ((s + 1.0) * t - s)

def back_out(t: float, s: float = 1.70158) -> float:
    t -= 1.0
    return t * t * ((s + 1.0) * t + s) + 1.0

def back_in_out(t: float, s: float = 1.70158) -> float:
    s *= 1.525
    if t < 0.5:
        t *= 2.0
        return 0.5 * (t * t * ((s + 1.0) * t - s))
    t = t * 2.0 - 2.0
    return 0.5 * (t * t * ((s + 1.0) * t + s) + 2.0)

def elastic_in(t: float) -> float:
    if t == 0.0:
        return 0.0
    if t == 1.0:
        return 1.0
    p = 0.3
    return -math.pow(2.0, 10.0 * (t - 1.0)) * math.sin((t - 1.0 - p / 4.0) * (2.0 * math.pi) / p)

def elastic_out(t: float) -> float:
    if t == 0.0:
        return 0.0
    if t == 1.0:
        return 1.0
    p = 0.3
    return math.pow(2.0, -10.0 * t) * math.sin((t - p / 4.0) * (2.0 * math.pi) / p) + 1.0

def elastic_in_out(t: float) -> float:
    if t == 0.0:
        return 0.0
    if t == 1.0:
        return 1.0
    p = 0.3 * 1.5
    if t < 0.5:
        t = t * 2.0 - 1.0
        return -0.5 * math.pow(2.0, 10.0 * t) * math.sin((t - p / 4.0) * (2.0 * math.pi) / p)
    t = t * 2.0 - 1.0
    return 0.5 * math.pow(2.0, -10.0 * t) * math.sin((t - p / 4.0) * (2.0 * math.pi) / p) + 1.0

def bounce_out(t: float) -> float:
    if t < 1.0 / 2.75:
        return 7.5625 * t * t
    elif t < 2.0 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375

def bounce_in(t: float) -> float:
    return 1.0 - bounce_out(1.0 - t)

def bounce_in_out(t: float) -> float:
    if t < 0.5:
        return bounce_in(t * 2.0) * 0.5
    return bounce_out(t * 2.0 - 1.0) * 0.5 + 0.5

_EASINGS = {
    "linear": linear,
    "quad_in": quad_in,
    "quad_out": quad_out,
    "quad_in_out": quad_in_out,
    "cubic_in": cubic_in,
    "cubic_out": cubic_out,
    "cubic_in_out": cubic_in_out,
    "quart_in": quart_in,
    "quart_out": quart_out,
    "quart_in_out": quart_in_out,
    "quint_in": quint_in,
    "quint_out": quint_out,
    "quint_in_out": quint_in_out,
    "sine_in": sine_in,
    "sine_out": sine_out,
    "sine_in_out": sine_in_out,
    "expo_in": expo_in,
    "expo_out": expo_out,
    "expo_in_out": expo_in_out,
    "circ_in": circ_in,
    "circ_out": circ_out,
    "circ_in_out": circ_in_out,
    "back_in": back_in,
    "back_out": back_out,
    "back_in_out": back_in_out,
    "elastic_in": elastic_in,
    "elastic_out": elastic_out,
    "elastic_in_out": elastic_in_out,
    "bounce_in": bounce_in,
    "bounce_out": bounce_out,
    "bounce_in_out": bounce_in_out,

    # CSS aliases
    "ease": cubic_in_out,
    "ease_in": cubic_in,
    "ease-in": cubic_in,
    "ease_out": cubic_out,
    "ease-out": cubic_out,
    "ease_in_out": cubic_in_out,
    "ease-in-out": cubic_in_out,
}

def get_easing(name: str) -> EasingFunction:
    if name in _EASINGS:
        return _EASINGS[name]
    raise ValueError(f"Unknown easing function: {name}")