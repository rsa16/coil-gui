import pygame
from coil_gui import UIManager, Container, Observable
from coil_gui.widgets import Button, Label
from coil_gui.layout import FlexLayout, FlexDirection, JustifyContent, AlignItems

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Coil GUI Binding & State Demo")
    clock = pygame.time.Clock()

    manager = UIManager(screen)

    # 1. Define styles
    manager.stylesheet.add_rule("Button", {
        "background_color": "#3498db",
        "color": "#ffffff",
        "border_radius": 10,
        "border_color": "#2980b9",
        "border_width": 2,
    })

    manager.stylesheet.add_rule("Button:hover", {
        "background_color": "#2980b9",
        "border_color": "#1f6391",
    })

    manager.stylesheet.add_rule("Button:active", {
        "background_color": "#1f6391",
        "border_color": "#154360",
    })

    # 2. Build UI
    root = Container(
        layout=FlexLayout(
            direction=FlexDirection.COLUMN,
            justify=JustifyContent.CENTER,
            align=AlignItems.CENTER,
            gap=20
        ),
        width=800,
        height=600
    )
    root.style.background_color = "#2c3e50"
    manager.set_root(root)

    # 3. State / Observable
    counter = Observable(0)

    # Title Label
    title = Label("Binding & State Demo")
    title.style.color = "#ecf0f1"
    title.style.font_size = 32
    root.add_child(title)

    # Counter Label bound to counter state
    counter_label = Label("Count: 0")
    counter_label.style.color = "#2ecc71"
    counter_label.style.font_size = 28
    counter_label.bind("text", counter, lambda val: f"Count: {val}")
    root.add_child(counter_label)

    # Button to increment counter
    btn_inc = Button("Increment Counter", width=220, height=50)
    btn_inc.style.padding = 15
    btn_inc.on_click = lambda: counter.set(counter.value + 1)
    root.add_child(btn_inc)

    # Button to reset counter
    btn_reset = Button("Reset Counter", width=220, height=50)
    btn_reset.style.padding = 15
    btn_reset.on_click = lambda: counter.set(0)
    root.add_child(btn_reset)

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