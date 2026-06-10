import pygame

from coil_gui import UIManager, StyleSheet, Container
from coil_gui.widgets import Label
from coil_gui.layout import AbsoluteLayout
from coil_gui.effects import DropShadow

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Coil GUI Basic Example")
    clock = pygame.time.Clock()

    # Create stylesheet
    stylesheet = StyleSheet()
    stylesheet.add_rule("Container", {"background_color": "#20232a"})
    stylesheet.add_rule("Label", {"color": "#61dafb", "font_size": 32})

    # Create manager with global stylesheet
    manager = UIManager(screen, stylesheet=stylesheet)

    # Create root container
    root = Container(layout=AbsoluteLayout(), x=0, y=0, width=800, height=600)

    # Create a sub-container with shadow
    panel = Container(x=200, y=150, width=400, height=300)
    panel.style.background_color = "#282c34"
    panel.effects += [
        DropShadow(offset=(0, 12), blur=40, spread=2, color=(0, 0, 0, 150))
    ]

    # Create label inside panel
    label = Label("Hello, Coil GUI!", x=50, y=120)

    panel.add_child(label)
    root.add_child(panel)

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
