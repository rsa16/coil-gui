# Coil GUI Layout System Guide

Coil GUI features a responsive layout system inspired by modern web (CSS Flexbox) and mobile framework patterns. This guide explains how widgets are sized, positioned, and how different layout managers work together to create dynamic user interfaces.

---

## 1. Core Concepts: Requested vs. Layout Dimensions

In a responsive UI, a widget's size is often not known until the layout phase. Coil GUI distinguishes between two types of dimensions:

### Requested Dimensions (`width`, `height`)
These are the values you set on a widget. They represent the **desired** size.
-   **Explicit Size**: If you set `width=100`, the widget asks to be 100 pixels wide.
-   **Automatic Size (`0`)**: If you leave `width` or `height` as `0` (the default), the widget is in **auto-sizing mode**. It will calculate its size based on its content or children.

### Layout Dimensions (`layout_width`, `layout_height`, `layout_x`, `layout_y`)
These are assigned by the **Layout Manager** during the layout phase.
-   A layout manager might override your requested size (e.g., if a widget is set to `stretch` or has `flex-grow`).
-   You should **always** use these properties (or the widget's render methods) when doing custom drawing or event handling, as they represent the actual state on screen.

---

## 2. The Measure Phase (Bottom-Up)

Before positioning widgets, the system needs to know how much space they need. This is the **Measure Phase**.

### `measure(available_w, available_h) -> Size`
Every widget has a `measure` method. It is called by parent layout managers to ask: *"Given this much available space, what is your preferred size?"*

-   **Base Widget**: Returns its requested `width` and `height`, clamped by its constraints.
-   **Label**: Returns the exact size of its text content.
-   **Container**: Asks its internal Layout Manager to measure its children and returns the total size needed to wrap them.

---

## 3. Layout Managers

Layout managers are responsible for taking a set of children and assigning them `layout` coordinates and dimensions.

### FlexLayout
Inspired by CSS Flexbox, `FlexLayout` is the most versatile manager. It arranges children in rows or columns.

**Key Container Properties:**
-   `direction`: `ROW` or `COLUMN`.
-   `justify`: `START`, `CENTER`, `END`, `SPACE_BETWEEN`, `SPACE_AROUND`, `SPACE_EVENLY`.
-   `align`: `START`, `CENTER`, `END`, `STRETCH` (cross-axis alignment).
-   `gap`: Space between children.
-   `wrap`: `NOWRAP` (default) or `WRAP`.

**Key Item Properties (via `widget.flex`):**
-   `grow`: How much of the remaining space the item should take.
-   `shrink`: How much the item should shrink if space is insufficient.
-   `basis`: The initial size of the item before growing/shrinking.

### AnchorLayout
Provides a way to position widgets relative to their parent's edges or other siblings.

-   **Edges**: `left`, `right`, `top`, `bottom`, `center_x`, `center_y`.
-   **Margins**: You can specify offsets from the anchored edges.
-   **Filling**: `anchors.fill(parent)` stretches the widget to fill the container.
-   **Centering**: `anchors.center_in(parent)` centers the widget.

### AbsoluteLayout
The simplest layout. It places children at their requested `x` and `y` coordinates.
-   If no `width`/`height` is set, the child will keep its measured size.
-   Positions are relative to the top-left of the container.

---

## 4. Building a Responsive UI

To make your UI responsive:

1.  **Use `0` for dimensions**: Let containers and labels calculate their own size.
2.  **Use `flex.grow = 1`**: Make elements expand to fill available space.
3.  **Nest Containers**: Combine `FlexLayout` columns and rows to create complex grids.
4.  **Use Constraints**: Set `min_width` or `max_height` to keep auto-sizing within reasonable bounds.

### Example: Auto-Sizing Card
```python
# This container will automatically grow its height to fit the title and content
card = Container(
    classes="card",
    layout=FlexLayout(direction=FlexDirection.COLUMN, gap=10)
)

card.add_child(Label("Dynamic Title", font_size=24))
card.add_child(Label("This is some long content that will expand the card's height."))
```
