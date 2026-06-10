import pygame
from coil_gui import UIManager, Container
from coil_gui.widgets import Button, Label
from coil_gui.layout import FlexLayout, FlexDirection, JustifyContent, AlignItems

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Coil GUI Button Demo")
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

    manager.stylesheet.add_rule(".danger", {
        "background_color": "#e74c3c",
        "border_color": "#c0392b",
    })

    manager.stylesheet.add_rule(".danger:hover", {
        "background_color": "#c0392b",
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

    title = Label("Button States Demo")
    title.style.color = "#ecf0f1"
    title.style.font_size = 32
    root.add_child(title)

    # Standard Button
    btn1 = Button("Standard Button", width=200, height=50)
    btn1.style.padding = 15
    btn1.on_click = lambda: print("Standard Button Clicked!")
    root.add_child(btn1)

    # Danger Button
    btn2 = Button("Danger Button", width=200, height=50, classes="danger")
    btn2.on_click = lambda: print("Danger Button Clicked!")
    root.add_child(btn2)

    # Disabled Button
    btn3 = Button("Disabled Button", width=200, height=50)
    btn3.disabled = True
    btn3.style.background_color = "#95a5a6"
    btn3.style.border_color = "#7f8c8d"
    btn3.style.color = "#bdc3c7"
    root.add_child(btn3)

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
