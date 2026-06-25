<div align="center">
  <h1>Coil GUI</h1>
  <p><strong>A modern, CSS-inspired GUI framework for Pygame Community Edition</strong></p>
  <p>
    <img src="https://img.shields.io/badge/python-≥3.13-blue" alt="Python 3.13+">
    <img src="https://img.shields.io/badge/version-0.1.0-orange" alt="Version 0.1.0">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
  </p>
</div>


## Why Coil GUI?

**There is no modern GUI framework for Pygame.** I found this out as I was attempting to create a GUI for a hackathon, where I was forced to create every rectangle for the buttons from scratch. Existing solutions like thorpy or pygame-gui are either overly simplistic or force you into a rigid and non-declarative style. Coil GUI was built for web developers wanting to use web UI concepts in a Pygame ecosystem.

If you want to be able to:
- Build a Pygame UI with CSS-like stylesheets and selectors (`.class`, `#id`, `:hover`, `:active`)
- Use a Flexbox layout sysem (+ others!) to create responsive interfaces
- Anime widget properties using easing functions, timelines, or CSS-style transitions
- Bind UI state to widgets reactively

...then Coil GUI is for you.


## Features

- **CSS-Inspired Styling** - Stylesheets with class, ID, and pseudo-class selectors (`:hover`, `:active`, `:disabled`, `:focused`). Theme variables support.
- **Flexbox Layout** - Full CSS Flexbox implementation with `FlexDirection`, `JustifyContent`, `AlignItems`, `FlexWrap`, `flex-grow`, `flex-shrink`, and `flex-basis`.
- **Anchor Layout** - Position widgets relative to parent edges or sibling widgets. Fill, center, or pin to any edge.
- **Absolute Layout** - Simple manual positioning with percentage-based sizing.
- **Reactive Data Binding** - `Observable` objects that automatically update widget properties when changed. Batch updates supported.
- **Animation System** - Tween any widget property (position, size, color, opacity, rotation, scale) with 30+ easing functions. Timelines for sequenced/parallel animations.
- **CSS Transitions** - Declarative style transitions: `"background_color 0.3s ease, scale 0.2s back_out"`
- **Visual Effects** - Drop shadows with configurable offset, blur, spread, and color.
- **18 Built-in Widgets** - Label, RichLabel, Button, Image, TextInput, Slider, ToggleSwitch, Checkbox, RadioButton, Dropdown, ColorPicker, SpinBox, ScrollView, ListView, Panel, Tabs, Modal, Tooltip.
- **Widget Lifecycle** - `on_mount()`, `on_unmount()`, `on_layout()`, `on_render_before()`, `on_render_after()` hooks.
- **Zero External Dependencies** - Only requires `pygame-ce` and `pydantic`.


## Installation

This project is still extremely alpha, and we have not yet published on PyPi. To install it:
```bash
pip install git+https://github.com/rsa16/coil-gui
```

**Requirements:**
- Python ≥ 3.13
- `pygame-ce` ≥ 2.5.7
- `pydantic` ≥ 2.13.4

## Quick Start

### Minimal Example

```python
import pygame
from coil_gui import UIManager, Container
from coil_gui.widgets import Label
from coil_gui.layout import AbsoluteLayout

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    manager = UIManager(screen)

    root = Container(layout=AbsoluteLayout(), width=800, height=600)
    root.style.background_color = "#20232a"

    label = Label("Hello, Coil GUI!", x=200, y=250)
    label.style.color = "#61dafb"
    label.style.font_size = 32
    root.add_child(label)

    manager.set_root(root)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.process_events(event)

        manager.update(dt)
        screen.fill((0, 0, 0))
        manager.draw_ui()
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
```

## Core Concepts

### The Widget Tree

Coil GUI uses a **widget tree,** which is a hierarchy of `Widget` and `Container` objects. The root is set via `manager.set_root(root)`. Each widget can have children, forming a tree that mirrors the visual layout.

```
UIManager
  └── Container (root)
       ├── Label
       ├── Button
       │    └── Label (inside button)
       └── Container (panel)
            ├── Label
            └── Slider
```

### The Game Loop

The standard Pygame loop integrates with Coil GUI through three calls:

```python
manager.process_events(event)   # Dispatch events to widgets
manager.update(dt)              # Update animations, layout, bindings
manager.draw_ui()               # Render the widget tree
```

### Requested vs. Layout Dimensions

Widgets have two sets of size properties:

- **`width` / `height`** — The *requested* size. Set to `0` for auto-sizing.
- **`layout_width` / `layout_height` / `layout_x` / `layout_y`** — The *actual* size and position assigned by the layout manager.

Percentage-based sizing is supported: `width="50%"` resolves to 50% of the parent's width.

### Styling System

Coil GUI has a three-tier styling system with clear precedence:

1. **Transition styles** (active CSS-style transitions)
2. **Inline styles** (set directly via `widget.style.property = value`)
3. **Computed styles** (from stylesheet rules, matched by selectors)
4. **Default values**

#### Stylesheets

```python
from coil_gui import StyleSheet

stylesheet = StyleSheet()
stylesheet.add_rule("Button", {
    "background_color": "#3498db",
    "color": "#ffffff",
    "border_radius": 10,
})
stylesheet.add_rule("Button:hover", {
    "background_color": "#2980b9",
})
stylesheet.add_rule(".danger", {
    "background_color": "#e74c3c",
})
stylesheet.add_rule("#submit-btn", {
    "font_size": 18,
})

manager = UIManager(screen, stylesheet=stylesheet)
```

**Selector syntax:**
| Pattern | Matches |
|---------|---------|
| `Button` | Widgets of class `Button` |
| `.classname` | Widgets with `classes="classname"` |
| `#widget_id` | Widget with `id="widget_id"` |
| `*` | All widgets |
| `Button:hover` | Button in hover state |
| `.danger:active` | Widget with class `danger` in active state |

#### Inline Styles

```python
widget.style.background_color = "#282c34"
widget.style.font_size = 24
widget.style.color = "#ffffff"
widget.style.border_radius = 8
widget.style.border_width = 2
widget.style.border_color = "#555555"
widget.style.padding = 10
```

#### Theme Variables

```python
from coil_gui import Theme

theme = Theme({"primary": "#3498db", "danger": "#e74c3c"})
manager = UIManager(screen, theme=theme)

# In stylesheet rules, reference theme variables with $ prefix:
stylesheet.add_rule("Button", {"background_color": "$primary"})
```

## Layout System

### FlexLayout (CSS Flexbox)

The most versatile layout manager. Arranges children in rows or columns.

```python
from coil_gui.layout import FlexLayout, FlexDirection, JustifyContent, AlignItems

container = Container(
    layout=FlexLayout(
        direction=FlexDirection.COLUMN,
        justify=JustifyContent.CENTER,
        align=AlignItems.STRETCH,
        gap=10,
        padding=20,
    )
)
```

**Per-child flex properties:**
```python
child.flex.grow = 1       # Take remaining space
child.flex.shrink = 0     # Don't shrink
child.flex.basis = 100    # Initial size before grow/shrink
```

### AnchorLayout

Position widgets relative to parent edges or sibling widgets.

```python
from coil_gui.layout import AnchorLayout

panel = Container(layout=AnchorLayout(), width=400, height=400)

# Pin to top-left with margin
box = Container(width=100, height=100)
box.anchors.top = panel.top
box.anchors.left = panel.left
box.anchors.margins = 20

# Center in parent
label.anchors.center_in(panel)

# Fill entire parent
child.anchors.fill(parent)

# Position relative to sibling
box2.anchors.left = box1.right
box2.anchors.left_margin = 20
```

### AbsoluteLayout

Simple manual positioning. Children are placed at their `x` and `y` coordinates.

```python
from coil_gui.layout import AbsoluteLayout

container = Container(layout=AbsoluteLayout())
child = Label("Hello", x=100, y=50)
```

## Widgets

Coil GUI ships with 18 built-in widgets, as of right now. A lot of these are still being developed, so expect bugs:

| Widget | Description |
|--------|-------------|
| `Label` | Text display with auto-sizing |
| `RichLabel` | Text with `[b]bold[/b]`, `[i]italic[/i]`, `[color=#hex]colored[/color]` markup |
| `Button` | Clickable button with hover/active/disabled states |
| `Image` | Display a `pygame.Surface` or image file |
| `TextInput` | Single-line text input with cursor, placeholder, and keyboard navigation |
| `Slider` | Horizontal value slider with draggable thumb |
| `ToggleSwitch` | On/off toggle with animated thumb |
| `Checkbox` | Check/uncheck toggle |
| `RadioButton` | Radio button with auto-exclusive groups |
| `Dropdown` | Expandable dropdown/select with popup list |
| `ColorPicker` | RGB color picker with sliders and hex input |
| `SpinBox` | Numeric input with increment/decrement buttons |
| `ScrollView` | Scrollable container with vertical scrollbar |
| `ListView` | Vertical list with custom item renderer |
| `Panel` | Container with title bar |
| `Tabs` | Tabbed container with clickable tab headers |
| `Modal` | Modal dialog with overlay, title bar, and close button |
| `Tooltip` | Hover tooltip with configurable delay |

### Widget Lifecycle

Widgets have lifecycle hooks that you can override:

```python
class MyWidget(Widget):
    def on_mount(self):
        """Called when added to a visible tree (has a manager)."""

    def on_unmount(self):
        """Called when removed from the tree."""

    def on_layout(self):
        """Called after layout is computed."""

    def on_render_before(self, surface):
        """Called before the widget's content and children are drawn."""

    def on_render_after(self, surface):
        """Called after the widget's content and children are drawn."""
```

## Data Binding

Reactive state management with `Observable`:

```python
from coil_gui import Observable

# Create observable state
counter = Observable(0)

# Bind a widget property to the observable
label.bind("text", counter, lambda val: f"Count: {val}")

# Update the state — the label updates automatically
counter.set(counter.value + 1)

# Or use the property setter
counter.value = 42
```

**Nested property paths** are supported:
```python
widget.bind("style.background_color", color_obs)
```

**Batch updates** prevent redundant notifications:
```python
from coil_gui import batch_updates

with batch_updates():
    counter.set(1)
    name.set("Alice")
    # Observers are notified once after the block exits
```

## Animation

### Tweening Properties

Animate any widget property with a tween:

```python
# Animate position
widget.animate("x", 300, duration=1.0, easing="bounce_out")

# Animate color (hex strings or rgba tuples)
widget.animate("style.background_color", "#e74c3c", duration=0.5)

# Animate with delay and callbacks
widget.animate(
    "opacity", 0.0, duration=0.3,
    easing="ease_in",
    delay=0.2,
    on_complete=lambda: print("Done!"),
    on_update=lambda val: print(f"Current: {val}")
)
```

### Easing Functions

30+ easing functions available:

| Category | Functions |
|----------|-----------|
| Linear | `linear` |
| Quadratic | `quad_in`, `quad_out`, `quad_in_out` |
| Cubic | `cubic_in`, `cubic_out`, `cubic_in_out` |
| Quartic | `quart_in`, `quart_out`, `quart_in_out` |
| Quintic | `quint_in`, `quint_out`, `quint_in_out` |
| Sine | `sine_in`, `sine_out`, `sine_in_out` |
| Exponential | `expo_in`, `expo_out`, `expo_in_out` |
| Circular | `circ_in`, `circ_out`, `circ_in_out` |
| Back | `back_in`, `back_out`, `back_in_out` |
| Elastic | `elastic_in`, `elastic_out`, `elastic_in_out` |
| Bounce | `bounce_in`, `bounce_out`, `bounce_in_out` |
| CSS Aliases | `ease`, `ease_in`, `ease-out`, `ease_in_out`, etc. |

### Timelines

Sequence or parallelize animations:

```python
from coil_gui.animation import Tween, Timeline

timeline = Timeline(loop=True)

# Run in parallel
timeline.parallel([
    Tween(box, "rotation", 360, duration=2.0, easing="linear"),
    Tween(box, "scale", 1.5, duration=1.0, easing="sine_in_out"),
])

# Run in sequence
timeline.sequence([
    Tween(box, "x", 100, duration=0.5, easing="quint_out"),
    Tween(box, "y", 200, duration=0.5, easing="quint_out"),
    Tween(box, "x", 0, duration=0.5, easing="quint_out"),
    Tween(box, "y", 0, duration=0.5, easing="quint_out"),
])

widget.anim_controller.add_timeline(timeline)
```

### CSS Transitions

Declarative style transitions — just like CSS:

```python
stylesheet.add_rule("Button", {
    "background_color": "#3498db",
    "transition": "background_color 0.3s ease, scale 0.2s back_out",
})

stylesheet.add_rule("Button:hover", {
    "background_color": "#2980b9",
    "scale": 1.05,
})
```

When the hover state changes, the `background_color` and `scale` properties animate smoothly.

## Visual Effects

### Drop Shadow

```python
from coil_gui.effects import DropShadow

panel.effects += [
    DropShadow(
        offset=(0, 12),    # Shadow offset
        blur=40,           # Blur radius
        spread=2,          # Spread amount
        color=(0, 0, 0, 150),  # RGBA color
    )
]
```

---

## Examples

The `examples/` directory contains runnable demos:

| Example | Description |
|---------|-------------|
| `basic.py` | Minimal hello world with styling and drop shadow |
| `button_demo.py` | Button states, hover/active pseudo-classes, class selectors |
| `flex_demo.py` | Flexbox layout: justify, grow, wrap, column |
| `anchor_demo.py` | Anchor layout: pinning, centering, relative positioning |
| `animation_demo.py` | Easing functions, multi-property animation, path following, staggered lists |
| `binding_demo.py` | Reactive data binding with Observable |
| `dropdown_demo.py` | Dropdown widget showcase |
| `lifecycle_demo.py` | Widget lifecycle hooks (mount, unmount, layout, render) |
| `widget_showcase.py` | All 18 widgets demonstrated in a polished UI |

Run any example:
```bash
python examples/basic.py
```

## Project Structure

```
coil-gui/
├── src/coil_gui/
│   ├── __init__.py          # Public API exports
│   ├── manager.py           # UIManager - main loop integration
│   ├── core/
│   │   ├── widget.py        # Base Widget class
│   │   └── container.py     # Container (widget with layout)
│   ├── layout/
│   │   ├── base.py          # Abstract Layout base class
│   │   ├── absolute.py      # AbsoluteLayout
│   │   ├── anchor.py        # AnchorLayout
│   │   ├── flex.py          # FlexLayout (CSS Flexbox)
│   │   └── constraints.py   # Size, Constraints models
│   ├── style/
│   │   ├── proxy.py         # Style resolution per-widget
│   │   ├── selector.py      # CSS-like selector matching
│   │   ├── stylesheet.py    # StyleSheet with rules
│   │   └── theme.py         # Theme variables
│   ├── binding/
│   │   ├── observable.py    # Observable with batch updates
│   │   └── binder.py        # bind() function
│   ├── animation/
│   │   ├── tween.py         # Property interpolation
│   │   ├── timeline.py      # Sequenced/parallel animations
│   │   ├── controller.py    # AnimationController per widget
│   │   ├── transition.py    # CSS-style transition manager
│   │   └── easing.py        # 30+ easing functions
│   ├── effects/
│   │   ├── base.py          # Abstract Effect base class
│   │   └── shadow.py        # DropShadow effect
│   ├── widgets/             # 18 built-in widgets
│   └── utils/               # Color, font, layout, math utilities
├── examples/                # Runnable demo scripts
└── docs/
    └── LAYOUT_GUIDE.md      # Detailed layout system documentation
```

## Architecture Principles

1. **Declarative over Imperative** — Describe *what* you want (stylesheets, layouts, bindings), not *how* to achieve it.
2. **CSS-Inspired, Python-Native** — Familiar concepts from web development (Flexbox, selectors, transitions) adapted for Python.
3. **Composable Widgets** — Widgets are building blocks. Compose them into complex UIs through nesting and layout managers.
4. **Separation of Concerns** — Styling, layout, animation, and data binding are independent systems that work together through the widget tree.
5. **Performance by Default** — Dirty-flagging ensures only changed widgets re-render. Layout is only recomputed when needed.


## License

MIT

## Contributing

Contributions are welcome! This project is in extremely early development (v0.1.0). Feel free to open issues, submit PRs, or suggest features.

**Author:** Rehan Ali ([rsa165.ali@gmail.com](mailto:rsa165.ali@gmail.com))
