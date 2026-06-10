class Selector:
    def __init__(self, pattern: str):
        self.pattern = pattern

    def matches(self, widget) -> bool:
        parts = self.pattern.split(':')
        base = parts[0]
        state = parts[1] if len(parts) > 1 else None

        match = False
        if base == "" or base == "*":
            match = True
        elif base.startswith("."):
            match = base[1:] in widget.classes
        elif base.startswith("#"):
            match = base[1:] == widget.id
        else:
            match = widget.__class__.__name__ == base

        if match and state:
            match = state in getattr(widget, 'state_flags', set())

        return match

    @property
    def specificity(self) -> int:
        s = 0
        if self.pattern.startswith("#"):
            s += 100
        elif self.pattern.startswith("."):
            s += 10
        elif self.pattern and not self.pattern.startswith("*"):
            s += 1
        if ":" in self.pattern:
            s += 10
        return s
