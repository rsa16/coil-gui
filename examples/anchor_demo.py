import pygame

from coil_gui import UIManager, Container
from coil_gui.widgets import Label
from coil_gui.layout import AnchorLayout

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.SCALED)
    pygame.display.set_caption("Coil GUI Anchor Layout Demo")
    clock = pygame.time.Clock()

    # Create manager
    manager = UIManager(screen)

    # Root container
    root = Container(layout=AnchorLayout(), width=800, height=600)
    manager.set_root(root)

    # A panel with AnchorLayout
    panel = Container(layout=AnchorLayout(), width=400, height=400)
    panel.style.background_color = "#282c34"
    panel.anchors.center_in(root)
    root.add_child(panel)

    # Box 1: Top-Left with margin
    box1 = Container(width=100, height=100)
    box1.style.background_color = "#ff4444"
    box1.anchors.top = panel.top
    box1.anchors.left = panel.left
    box1.anchors.margins = 20
    panel.add_child(box1)

    # Box 2: Relative to Box 1
    box2 = Container(width=100, height=100)
    box2.style.background_color = "#44ff44"
    box2.anchors.top = box1.top
    box2.anchors.left = box1.right
    box2.anchors.left_margin = 20
    panel.add_child(box2)

    # Label: Centered in panel
    label = Label("Centered Label")
    label.style.color = "#ffffff"
    label.style.font_size = 24
    label.anchors.center_in(panel)
    panel.add_child(label)

    # Box 3: Bottom-Right using origin
    box3 = Container(width=50, height=50)
    box3.style.background_color = "#4444ff"
    box3.anchors.bottom = panel.bottom
    box3.anchors.right = panel.right
    panel.add_child(box3)

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
