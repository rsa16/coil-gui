import pygame
from coil_gui import UIManager, Container, StyleSheet
from coil_gui.widgets import Button, Label
from coil_gui.layout import FlexLayout, FlexDirection, JustifyContent, AlignItems
from coil_gui.animation import Tween, Timeline

def create_section_header(title_text):
    label = Label(title_text)
    label.style.font_size = 18
    label.style.color = "#3498db"
    return label

def create_easing_box(parent, color, easing_name, label_text):
    # Container for easing box - height is still somewhat fixed for the track
    container = Container(
        layout=FlexLayout(direction=FlexDirection.COLUMN, align=AlignItems.CENTER, gap=2),
        width=100
    )

    label = Label(label_text)
    label.style.font_size = 12
    label.style.color = "#bdc3c7"
    container.add_child(label)

    track = Container(width=40, height=100)
    track.style.background_color = "#1a252f"
    track.style.border_radius = 20
    track.style.border_color = "#34495e"
    track.style.border_width = 1
    container.add_child(track)

    box = Container(width=30, height=30)
    box.style.background_color = color
    box.style.border_radius = 15
    box.x = 5
    box.y = 5
    track.add_child(box)

    t1 = Tween(box, "y", 65, duration=1.5, easing=easing_name)
    t2 = Tween(box, "y", 5, duration=1.5, easing=easing_name)

    timeline = Timeline(loop=True)
    timeline.sequence([t1, t2])
    box.anim_controller.add_timeline(timeline)

    parent.add_child(container)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Coil GUI Dynamic Animation Demo")
    clock = pygame.time.Clock()

    stylesheet = StyleSheet()
    stylesheet.add_rule("Container", {"background_color": "#2c3e50"})
    stylesheet.add_rule(".card", {
        "background_color": "#34495e",
        "border_radius": 10,
        "padding": 10,
        "border_color": "#2c3e50",
        "border_width": 1,
        "margin_bottom": 10
    })
    stylesheet.add_rule("Button", {
        "background_color": "#2980b9",
        "color": "#ffffff",
        "border_radius": 5,
        "padding": 8,
        "transition": "background_color 0.2s ease, scale 0.2s back_out"
    })

    manager = UIManager(screen, stylesheet=stylesheet)

    # Root container now with auto-height behavior (though limited by screen)
    root = Container(
        layout=FlexLayout(direction=FlexDirection.COLUMN, padding=15, gap=10, align=AlignItems.STRETCH),
        width=800
    )
    manager.set_root(root)

    # Header - No height set, will auto-size
    header = Container(layout=FlexLayout(direction=FlexDirection.COLUMN, align=AlignItems.CENTER, gap=2))
    root.add_child(header)
    title = Label("Dynamic Animation Layout")
    title.style.color = "#ecf0f1"
    title.style.font_size = 28
    header.add_child(title)
    sub = Label("Auto-sizing containers based on content")
    sub.style.color = "#95a5a6"
    sub.style.font_size = 14
    header.add_child(sub)

    # --- Section 1: Easing Grid ---
    # No height set, will auto-size based on easing_row
    s1 = Container(classes="card", layout=FlexLayout(direction=FlexDirection.COLUMN, align=AlignItems.CENTER, gap=5))
    root.add_child(s1)
    s1.add_child(create_section_header("I. Easing Functions"))

    easing_row = Container(layout=FlexLayout(direction=FlexDirection.ROW, justify=JustifyContent.CENTER, gap=30))
    s1.add_child(easing_row)

    create_easing_box(easing_row, "#e74c3c", "linear", "Linear")
    create_easing_box(easing_row, "#3498db", "cubic_in_out", "Cubic")
    create_easing_box(easing_row, "#2ecc71", "elastic_out", "Elastic")
    create_easing_box(easing_row, "#f1c40f", "bounce_out", "Bounce")

    # --- Row 2: Combined Animations ---
    row2 = Container(layout=FlexLayout(direction=FlexDirection.ROW, gap=10))
    root.add_child(row2)

    # Section 2: The "Transformer"
    # Flex grow=1 to take half width
    s2 = Container(classes="card", layout=FlexLayout(direction=FlexDirection.COLUMN, align=AlignItems.CENTER, gap=5))
    s2.flex.grow = 1
    row2.add_child(s2)
    s2.add_child(create_section_header("II. Multi-Property"))
    transformer_cont = Container(width=80, height=80)
    s2.add_child(transformer_cont)
    transformer = Container(width=40, height=40)
    transformer.style.background_color = "#9b59b6"
    transformer.style.border_radius = 5
    transformer.origin = (0.5, 0.5)
    transformer.x = 40
    transformer.y = 40
    transformer_cont.add_child(transformer)

    tl_trans = Timeline(loop=True)
    tl_trans.add(Tween(transformer, "rotation", 360, duration=3.0, easing="linear"))
    tl_trans.sequence([
        Tween(transformer, "scale", 1.5, duration=1.5, easing="sine_in_out"),
        Tween(transformer, "scale", 1.0, duration=1.5, easing="sine_in_out"),
    ])
    transformer.anim_controller.add_timeline(tl_trans)

    # Section 3: The Path Follower
    s3 = Container(classes="card", layout=FlexLayout(direction=FlexDirection.COLUMN, align=AlignItems.CENTER, gap=5))
    s3.flex.grow = 1
    row2.add_child(s3)
    s3.add_child(create_section_header("III. Path Following"))
    path_track = Container(width=150, height=80)
    path_track.style.background_color = "#1a252f"
    path_track.style.border_radius = 5
    s3.add_child(path_track)
    p_dot = Container(width=12, height=12)
    p_dot.style.background_color = "#ecf0f1"
    p_dot.style.border_radius = 3
    path_track.add_child(p_dot)

    tl_path = Timeline(loop=True)
    tl_path.sequence([
        Tween(p_dot, "x", 128, duration=0.8, easing="quint_out", on_complete=lambda: setattr(p_dot.style, "background_color", "#e74c3c")),
        Tween(p_dot, "y", 58, duration=0.6, easing="quint_out", on_complete=lambda: setattr(p_dot.style, "background_color", "#f1c40f")),
        Tween(p_dot, "x", 10, duration=0.8, easing="quint_out", on_complete=lambda: setattr(p_dot.style, "background_color", "#2ecc71")),
        Tween(p_dot, "y", 10, duration=0.6, easing="quint_out", on_complete=lambda: setattr(p_dot.style, "background_color", "#ecf0f1")),
    ])
    p_dot.anim_controller.add_timeline(tl_path)

    # --- Section 4: Staggered List ---
    s4 = Container(classes="card", layout=FlexLayout(direction=FlexDirection.COLUMN, align=AlignItems.CENTER, gap=10))
    root.add_child(s4)
    s4.add_child(create_section_header("IV. Staggered Entrance"))
    list_row = Container(layout=FlexLayout(direction=FlexDirection.ROW, gap=8, justify=JustifyContent.CENTER))
    s4.add_child(list_row)
    list_items = []
    for _ in range(8):
        item = Container(width=40, height=20)
        item.style.background_color = "#3498db"
        item.style.border_radius = 3
        item.opacity = 0.0
        item.scale = 0.5
        list_row.add_child(item)
        list_items.append(item)

    def play_staggered():
        for i, item in enumerate(list_items):
            item.opacity = 0.0
            item.scale = 0.5
            item.anim_controller.stop_all()
            item.animate("opacity", 1.0, duration=0.4, delay=i * 0.05)
            item.animate("scale", 1.0, duration=0.4, delay=i * 0.05, easing="back_out")

    play_staggered()
    replay_btn = Button("Replay Sequence", on_click=play_staggered)
    s4.add_child(replay_btn)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                root.width = event.w
                root.height = event.h
                root.set_layout_box(0, 0, event.w, event.h)
            manager.process_events(event)

        manager.update(dt)
        screen.fill((20, 30, 40))
        manager.draw_ui()
        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    main()
