import re
from typing import Any, Dict, Optional, Tuple, Union
from .tween import Tween
from .easing import get_easing

# Regex to parse transition shorthand: "property duration [easing] [delay]"
# e.g., "background_color 0.3s ease_in_out 0.1s" or "opacity 200ms"
TRANSITION_RE = re.compile(
    r"([a-zA-Z_][a-zA-Z0-9_]*)\s+([\d\.]+m?s)(?:\s+([a-zA-Z_][a-zA-Z0-9_]*))?(?:\s+([\d\.]+m?s))?"
)

def parse_duration(val: str) -> float:
    if val.endswith("ms"):
        return float(val[:-2]) / 1000.0
    if val.endswith("s"):
        return float(val[:-1])
    return float(val)

class TransitionSpec:
    def __init__(self, property_name: str, duration: float, easing: str = "linear", delay: float = 0.0):
        self.property_name = property_name
        self.duration = duration
        self.easing = easing
        self.delay = delay

def parse_transitions(transition_str: str) -> Dict[str, TransitionSpec]:
    specs = {}
    # Support comma-separated transitions
    parts = transition_str.split(",")
    for part in parts:
        part = part.strip()
        match = TRANSITION_RE.match(part)
        if match:
            prop, dur_str, easing, delay_str = match.groups()
            duration = parse_duration(dur_str)
            easing = easing or "linear"
            delay = parse_duration(delay_str) if delay_str else 0.0
            specs[prop] = TransitionSpec(prop, duration, easing, delay)
    return specs

class TransitionManager:
    def __init__(self, widget: Any):
        self.widget = widget
        self.active_transitions: Dict[str, Tween] = {}

    def handle_style_change(self, old_style: Dict[str, Any], new_style: Dict[str, Any]):
        # Check if transition is defined
        transition_str = new_style.get("transition") or self.widget.style._inline_styles.get("transition")
        if not transition_str:
            # Clean up any active transitions if transition is removed
            for prop in list(self.active_transitions.keys()):
                self.stop_transition(prop)
            return

        specs = parse_transitions(transition_str)

        for prop, spec in specs.items():
            # We only transition if the property actually changed in the computed style
            old_val = old_style.get(prop)
            new_val = new_style.get(prop)

            if old_val is not None and new_val is not None and old_val != new_val:
                # If there's already an active transition for this property, we want to start
                # the new transition from the CURRENT transitioned value, not the old computed value!
                current_val = self.widget.style._transition_styles.get(prop, old_val)

                self.start_transition(prop, current_val, new_val, spec)

    def start_transition(self, prop: str, start_val: Any, end_val: Any, spec: TransitionSpec):
        self.stop_transition(prop)

        # We animate the property inside self.widget.style._transition_styles
        # So we create a target object or use a custom on_update callback
        def on_update(val):
            self.widget.style._transition_styles[prop] = val
            self.widget.mark_render_dirty()
            if prop in ("width", "height", "padding", "margin", "gap"):
                self.widget.mark_layout_dirty()

        def on_complete():
            if prop in self.widget.style._transition_styles:
                del self.widget.style._transition_styles[prop]
            if prop in self.active_transitions:
                del self.active_transitions[prop]
            self.widget.mark_render_dirty()
            self.widget.mark_layout_dirty()

        # Set initial transition value
        self.widget.style._transition_styles[prop] = start_val

        tween = Tween(
            target=self.widget.style._transition_styles,
            property_name=prop,
            end_value=end_val,
            duration=spec.duration,
            start_value=start_val,
            easing=spec.easing,
            delay=spec.delay,
            on_complete=on_complete,
            on_update=on_update,
        )
        self.active_transitions[prop] = tween

    def stop_transition(self, prop: str):
        if prop in self.active_transitions:
            # Do not trigger on_complete, just remove
            if prop in self.widget.style._transition_styles:
                del self.widget.style._transition_styles[prop]
            del self.active_transitions[prop]

    def update(self, dt: float):
        if not self.active_transitions:
            return

        still_active = {}
        for prop, tween in list(self.active_transitions.items()):
            done = tween.update(dt)
            if not done:
                still_active[prop] = tween
        self.active_transitions = still_active
