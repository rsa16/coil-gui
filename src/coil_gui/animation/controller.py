from typing import List, Dict, Any, Union, Callable, Optional
from .tween import Tween
from .timeline import Timeline
from .easing import EasingFunction

class AnimationController:
    def __init__(self, widget: Any):
        self.widget = widget
        self.active_tweens: List[Tween] = []
        self.active_timelines: List[Timeline] = []

    def animate(
        self,
        property_name: str,
        end_value: Any,
        duration: float,
        easing: Union[str, EasingFunction] = "linear",
        delay: float = 0.0,
        on_complete: Optional[Callable[[], None]] = None,
        on_update: Optional[Callable[[Any], None]] = None,
    ) -> Tween:
        """
        Animates a property of the widget. Stops any existing tween on the same property.
        """
        self.stop_property(property_name)

        tween = Tween(
            target=self.widget,
            property_name=property_name,
            end_value=end_value,
            duration=duration,
            easing=easing,
            delay=delay,
            on_complete=on_complete,
            on_update=on_update,
        )
        self.active_tweens.append(tween)
        self.widget.mark_render_dirty()
        if property_name in ("x", "y", "width", "height", "scale", "rotation") or property_name.startswith("style."):
            self.widget.mark_layout_dirty()
        return tween

    def add_timeline(self, timeline: Timeline):
        self.active_timelines.append(timeline)
        self.widget.mark_render_dirty()
        self.widget.mark_layout_dirty()

    def stop_property(self, property_name: str):
        """
        Stops any active tween animating the specified property.
        """
        self.active_tweens = [t for t in self.active_tweens if t.property_name != property_name]

    def stop_all(self):
        self.active_tweens.clear()
        self.active_timelines.clear()

    def update(self, dt: float):
        if not self.active_tweens and not self.active_timelines:
            return

        # Update tweens
        still_active_tweens = []
        for tween in self.active_tweens:
            done = tween.update(dt)
            if not done:
                still_active_tweens.append(tween)
        self.active_tweens = still_active_tweens

        # Update timelines
        still_active_timelines = []
        for timeline in self.active_timelines:
            done = timeline.update(dt)
            if not done:
                still_active_timelines.append(timeline)
        self.active_timelines = still_active_timelines

        # Mark widget dirty if there are active animations
        if self.active_tweens or self.active_timelines:
            self.widget.mark_render_dirty()
            self.widget.mark_layout_dirty()