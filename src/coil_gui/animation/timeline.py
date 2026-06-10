from typing import List, Union, Callable, Optional
from .tween import Tween

class Timeline:
    def __init__(self, loop: bool = False, on_complete: Optional[Callable[[], None]] = None):
        self.loop = loop
        self.on_complete = on_complete
        self.tweens: List[Tween] = []
        self.active_tweens: List[Tween] = []
        self.completed = False
        self.paused = False

        # For sequential/parallel groups
        self._sequences: List[List[Tween]] = []
        self._current_sequence_index = 0

    def add(self, tween: Tween) -> 'Timeline':
        self.tweens.append(tween)
        self.active_tweens.append(tween)
        return self

    def sequence(self, tweens: List[Tween]) -> 'Timeline':
        """
        Adds a sequence of tweens that will run one after another.
        """
        if not tweens:
            return self
        self._sequences.append(tweens)
        # Only the first tween in the sequence is active initially
        self.active_tweens.append(tweens[0])
        return self

    def parallel(self, tweens: List[Tween]) -> 'Timeline':
        """
        Adds a group of tweens that will run in parallel.
        """
        for tween in tweens:
            self.add(tween)
        return self

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.active_tweens.clear()
        self.tweens.clear()
        self._sequences.clear()
        self.completed = True

    def restart(self):
        self.completed = False
        self.paused = False
        self._current_sequence_index = 0
        # Reset all tweens
        for tween in self.tweens:
            tween.elapsed = 0.0
            tween.started = False
            tween.completed = False
        for seq in self._sequences:
            for tween in seq:
                tween.elapsed = 0.0
                tween.started = False
                tween.completed = False

        self.active_tweens = list(self.tweens)
        for seq in self._sequences:
            if seq:
                self.active_tweens.append(seq[0])

    def update(self, dt: float) -> bool:
        if self.paused or self.completed:
            return self.completed

        # Update active tweens
        still_active = []
        for tween in self.active_tweens:
            done = tween.update(dt)
            if done:
                # Check if this tween was part of a sequence
                for seq in self._sequences:
                    if tween in seq:
                        idx = seq.index(tween)
                        if idx + 1 < len(seq):
                            # Activate next tween in sequence
                            still_active.append(seq[idx + 1])
            else:
                still_active.append(tween)

        self.active_tweens = still_active

        # Check if everything is done
        all_done = len(self.active_tweens) == 0
        if all_done:
            if self.loop:
                self.restart()
            else:
                self.completed = True
                if self.on_complete:
                    self.on_complete()

        return self.completed