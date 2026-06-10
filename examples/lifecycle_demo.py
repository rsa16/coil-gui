import pygame

from coil_gui.manager import UIManager
from coil_gui.core.widget import Widget
from coil_gui.core.container import Container
from coil_gui.layout.flex import FlexLayout

class LifecycleWidget(Widget):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.style.background_color = "#333333"

    def on_mount(self):
        print(f"[{self.name}] Mounted!")

    def on_unmount(self):
        print(f"[{self.name}] Unmounted!")

    def on_layout(self):
        print(f"[{self.name}] Layout computed: {self.x}, {self.y}, {self.width}x{self.height}")

    def on_render_before(self, surface):
        abs_x, abs_y = self.get_absolute_position()
        pygame.draw.circle(surface, (0, 0, 255), (int(abs_x), int(abs_y)), 8)

    def on_render_after(self, surface):
        abs_x, abs_y = self.get_absolute_position()
        pygame.draw.circle(surface, (255, 0, 0), (int(abs_x), int(abs_y)), 5)

def main():
    pygame.init()
    screen = pygame.display.set_caption("Lifecycle Demo")
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    manager = UIManager(screen)

    root = Container(
        layout=FlexLayout(direction="column", gap=10, padding=20),
        width=800, height=600
    )
    manager.set_root(root)

    print("--- Adding Child 1 ---")
    child1 = LifecycleWidget("Child 1", width=100, height=50)
    root.add_child(child1)

    print("--- Adding Child 2 (nested) ---")
    child2 = LifecycleWidget("Child 2", width=100, height=50)
    nested_container = Container(width=150, height=100)
    nested_container.style.background_color = "#444444"
    nested_container.add_child(child2)
    root.add_child(nested_container)

    running = True
    frame_count = 0
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.process_events(event)

        manager.update(dt)

        screen.fill((200, 200, 200))
        manager.draw_ui()
        pygame.display.flip()

        if frame_count == 2:
            print("--- Removing Child 1 ---")
            root.remove_child(child1)

        if frame_count == 4:
            print("--- Re-adding Child 1 ---")
            root.add_child(child1)

        if frame_count == 6:
            running = False

        frame_count += 1

    pygame.quit()

if __name__ == "__main__":
    main()
