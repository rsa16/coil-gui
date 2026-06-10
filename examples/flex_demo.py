import pygame

from coil_gui import UIManager, Container
from coil_gui.widgets import Label
from coil_gui.layout import FlexLayout, FlexDirection, JustifyContent, AlignItems, FlexWrap

def create_box(width, height, color):
    box = Container(width=width, height=height)
    box.style.background_color = color
    return box

def main():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768), pygame.SCALED)
    pygame.display.set_caption("Coil GUI Flex Layout Demo")
    clock = pygame.time.Clock()

    # Create manager
    manager = UIManager(screen)

    # Root container (Column flex to stack different demos)
    root = Container(
        layout=FlexLayout(
            direction=FlexDirection.COLUMN,
            justify=JustifyContent.START,
            align=AlignItems.STRETCH,
            gap=20,
            padding=20,
        ),
        width=1024,
        height=768
    )
    root.style.background_color = "#1e1e1e"
    manager.set_root(root)

    # --- Demo 1: Row with Justify Center and Gap ---
    row1_label = Label("Row: Justify Center, Gap 10")
    row1_label.style.color = "#ffffff"
    root.add_child(row1_label)

    row1 = Container(
        layout=FlexLayout(direction=FlexDirection.ROW, justify=JustifyContent.CENTER, gap=10),
        height=60
    )
    row1.style.background_color = "#2d2d2d"
    row1.add_child(create_box(50, 40, "#ff4444"))
    row1.add_child(create_box(50, 40, "#44ff44"))
    row1.add_child(create_box(50, 40, "#4444ff"))
    root.add_child(row1)

    # --- Demo 2: Row with Space Between ---
    row2_label = Label("Row: Space Between")
    row2_label.style.color = "#ffffff"
    root.add_child(row2_label)

    row2 = Container(
        layout=FlexLayout(direction=FlexDirection.ROW, justify=JustifyContent.SPACE_BETWEEN),
        height=60
    )
    row2.style.background_color = "#2d2d2d"
    row2.add_child(create_box(50, 40, "#ff4444"))
    row2.add_child(create_box(50, 40, "#44ff44"))
    row2.add_child(create_box(50, 40, "#4444ff"))
    root.add_child(row2)

    # --- Demo 3: Flex Grow ---
    row3_label = Label("Row: Flex Grow (Middle box grows 1, others 0)")
    row3_label.style.color = "#ffffff"
    root.add_child(row3_label)

    row3 = Container(
        layout=FlexLayout(direction=FlexDirection.ROW, gap=10),
        height=60
    )
    row3.style.background_color = "#2d2d2d"
    row3.add_child(create_box(50, 40, "#ff4444"))

    growing_box = create_box(50, 40, "#44ff44")
    growing_box.flex.grow = 2
    row3.add_child(growing_box)

    row3.add_child(create_box(50, 40, "#4444ff"))
    root.add_child(row3)

    # --- Demo 4: Wrap ---
    row4_label = Label("Row: Wrap (Many boxes)")
    row4_label.style.color = "#ffffff"
    root.add_child(row4_label)

    row4 = Container(
        layout=FlexLayout(direction=FlexDirection.ROW, wrap=FlexWrap.WRAP, gap=10),
        height=150
    )
    row4.style.background_color = "#2d2d2d"
    for i in range(15):
        row4.add_child(create_box(100, 40, f"hsl({i * 24}, 70%, 50%)"))
    root.add_child(row4)

    # --- Demo 5: Column and Align Items Stretch ---
    col_demo_label = Label("Column: Align Items Stretch")
    col_demo_label.style.color = "#ffffff"
    root.add_child(col_demo_label)

    col1 = Container(
        layout=FlexLayout(direction=FlexDirection.COLUMN, align=AlignItems.STRETCH, gap=5),
        height=200,
        width=200
    )
    col1.style.background_color = "#2d2d2d"
    col1.add_child(create_box(50, 30, "#ff4444"))
    col1.add_child(create_box(50, 30, "#44ff44"))
    col1.add_child(create_box(50, 30, "#4444ff"))
    root.add_child(col1)

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
