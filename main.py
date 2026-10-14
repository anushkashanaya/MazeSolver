
import csv
from pathlib import Path
from collections import deque
import random
import argparse
import pygame

def load_maze(filename):
    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        maze = [[cell.strip() for cell in row] for row in reader if row]

    if not maze:
        raise ValueError("The maze file is empty.")

    n = len(maze)

    for row in maze:
        if len(row) != n:
            raise ValueError("The maze must be an N x N grid.")

    starts = []
    exits = []

    for r in range(n):
        for c in range(n):
            if maze[r][c] == "S":
                starts.append((r, c))
            elif maze[r][c] == "X":
                exits.append((r, c))

    if len(starts) != 1:
        raise ValueError("The maze must contain exactly one S.")

    if len(exits) != 1:
        raise ValueError("The maze must contain exactly one E.")

    return maze, starts[0], exits[0]


def solve_maze(maze, start, exit_position):
    n = len(maze)

    # Each state is (row, column, keys_collected)
    start_state = (start[0], start[1], 0)

    queue = deque([(start_state, 0)])
    visited = {start_state}
    parent = {start_state: None}

    directions = [
        (-1, 0),  # Up
        (1, 0),   # Down
        (0, -1),  # Left
        (0, 1)    # Right
    ]

    while queue:
        state, distance = queue.popleft()
        r, c, keys = state

        # Have we reached the exit?
        if (r, c) == exit_position:
            path = []

            while state is not None:
                path.append((state[0], state[1]))
                state = parent[state]

            path.reverse()
            return distance, path

        # Explore the four neighbouring cells
        for dr, dc in directions:
            nr = r + dr
            nc = c + dc

            # Reject moves outside the grid
            if not (0 <= nr < n and 0 <= nc < n):
                continue

            cell = maze[nr][nc]

            # Walls cannot be entered
            if cell == "#":
                continue

            new_keys = keys

            # Collect a key: a=0, b=1, ..., f=5
            if cell in "abcdef":
                key_index = ord(cell) - ord("a")
                new_keys |= (1 << key_index)

            # A door requires its matching key
            if cell in "ABCDEF":
                key_index = ord(cell) - ord("A")

                if not (new_keys & (1 << key_index)):
                    continue

            next_state = (nr, nc, new_keys)

            if next_state in visited:
                continue

            visited.add(next_state)
            parent[next_state] = state
            queue.append((next_state, distance + 1))

    # No valid path exists
    return -1, []


def save_solution_csv(maze, path, output_file):
    # Make a copy so the original maze remains unchanged
    solved_maze = [row[:] for row in maze]

    # Mark the shortest path with x
    for r, c in path:
        if solved_maze[r][c] == ".":
            solved_maze[r][c] = "x"

    # Create the output folder if it does not exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write the solved maze to a CSV file
    with open(
        output_file, "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerows(solved_maze)

    print("Solved maze saved to:", output_file)


def generate_maze(n=15, key_count=3, seed=None):
    """
    Generate a maze with a guaranteed route.
    Keys are placed before their matching doors.
    """
    if not 1 <= key_count <= 6:
        raise ValueError(
            "This version supports 1 to 6 key types."
        )

    if n < 7 or n % 2 == 0:
        raise ValueError(
            "Maze size must be odd and at least 7."
        )

    if n < 7:
        raise ValueError("Maze size must be at least 7.")

    rng = random.Random(seed)

    # Begin with a grid full of walls
    maze = [["#" for _ in range(n)] for _ in range(n)]

    # Build a winding corridor through alternating rows
    route = []

    for r in range(0, n, 2):
        columns = range(n) if (r // 2) % 2 == 0 else range(n - 1, -1, -1)

        for c in columns:
            maze[r][c] = "."
            route.append((r, c))

        # Connect this row to the next row
        if r + 1 < n:
            connector_c = n - 1 if (r // 2) % 2 == 0 else 0
            maze[r + 1][connector_c] = "."
            route.append((r + 1, connector_c))

    start = route[0]
    exit_position = route[-1]

    maze[start[0]][start[1]] = "S"
    maze[exit_position[0]][exit_position[1]] = "X"

        # Place keys and matching doors in route order.
    available = route[1:-1]
    spacing = len(available) // (2 * key_count + 1)

    for i in range(key_count):
        key_pos = available[(2 * i) * spacing]
        door_pos = available[(2 * i + 1) * spacing]

        key_letter = chr(ord("a") + i)
        door_letter = key_letter.upper()

        maze[key_pos[0]][key_pos[1]] = key_letter
        maze[door_pos[0]][door_pos[1]] = door_letter

    # Open a few additional cells to vary the maze.
    # Never overwrite the guaranteed route.
    route_set = set(route)

    for r in range(n):
        for c in range(n):
            if (r, c) not in route_set and rng.random() < 0.12:
                maze[r][c] = "."

    return maze, start, exit_position

    
def test_generator():
    for t in range(1, 5):
        maze, start, exit_position = generate_maze(
            n=15, key_count=t, seed=42
        )

        distance, path = solve_maze(
            maze, start, exit_position
        )

        assert distance >= 0, f"Maze with T={t} is unsolvable!"
        assert path[0] == start
        assert path[-1] == exit_position

        print(
            f"T={t}: solvable, distance={distance}, "
            f"path length={len(path)}"
        )




def visualize_maze(maze, path):
    pygame.init()

    n = len(maze)
    cell_size = max(24, min(48, 600 // n))
    margin = 25
    panel_width = 250

    grid_width = n * cell_size
    grid_height = n * cell_size
    panel_x = margin + grid_width + 25

    window_width = panel_x + panel_width + margin
    window_height = max(grid_height + 2 * margin, 470)

    screen = pygame.display.set_mode(
        (window_width, window_height)
    )
    pygame.display.set_caption("Maze Solver | Keys and Doors")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", max(14, cell_size // 2))
    small_font = pygame.font.SysFont("Arial", 16)
    title_font = pygame.font.SysFont("Arial", 23, bold=True)

    # Colors
    BACKGROUND = (238, 242, 247)
    WHITE = (255, 255, 255)
    BLACK = (38, 38, 42)
    GRID_LINE = (190, 196, 205)
    GREEN = (65, 185, 105)
    RED = (225, 80, 85)
    PATH_COLOR = (150, 220, 245)
    VISITED_COLOR = (70, 175, 220)
    PLAYER_COLOR = (35, 80, 210)
    TEXT_COLOR = (35, 40, 50)
    MUTED = (100, 110, 125)

    pair_colors = {
        "a": (255, 215, 95),
        "b": (185, 150, 240),
        "c": (255, 160, 110),
        "d": (105, 205, 185),
        "e": (240, 150, 195),
        "f": (145, 190, 255),
    }

    # E is reserved for the exit in the current input format.
    exit_position = next(
        (
            (r, c)
            for r in range(n)
            for c in range(n)
            if maze[r][c] == "X"
        ),
        None,
    )

    # Animation state
    step = 0
    paused = False
    delay_ms = 250
    elapsed_ms = 0
    finished = len(path) <= 1
    running = True

    # Show the full path from the beginning.
    full_path = set(path)

    def draw_text(text, x, y, selected_font, color=TEXT_COLOR):
        image = selected_font.render(
            str(text), True, color
        )
        screen.blit(image, (x, y))

    def collected_keys_at(current_step):
        keys = set()

        for r, c in path[:current_step + 1]:
            cell = maze[r][c]

            if cell in "abcdef":
                keys.add(cell)

        return keys

    def draw_frame():
        screen.fill(BACKGROUND)

        inventory = collected_keys_at(step)
        traversed = set(path[:step + 1])
        current_position = path[step] if path else None

        # Draw the maze grid
        for r in range(n):
            for c in range(n):
                cell = maze[r][c]

                x = margin + c * cell_size
                y = margin + r * cell_size

                color = WHITE
                label = cell

                if cell == "#":
                    color = BLACK

                elif cell == "S":
                    color = GREEN

                
                elif cell == "X":
                    color = RED
                    label = "E"

                elif cell in "abcdef":
                    if cell in inventory:
                        color = WHITE
                        label = ""
                    else:
                        color = pair_colors[cell]

                elif cell in "ABCDEF":
                    # These door symbols are unambiguous
                    # under the current E=exit convention.
                    key = cell.lower()

                    if key in inventory:
                        color = WHITE
                        label = "✓"
                    else:
                        color = pair_colors[key]

                # Highlight the full path underneath
                # the cell's original identity.
                if (r, c) in full_path and cell == ".":
                    color = PATH_COLOR

                # Highlight cells already traversed.
                if (r, c) in traversed and cell == ".":
                    color = VISITED_COLOR

                pygame.draw.rect(
                    screen,
                    color,
                    (x, y, cell_size, cell_size),
                )

                pygame.draw.rect(
                    screen,
                    GRID_LINE,
                    (x, y, cell_size, cell_size),
                    1,
                )

                if label:
                    text_color = (
                        WHITE if cell == "#" else TEXT_COLOR
                    )

                    image = font.render(
                        label, True, text_color
                    )

                    screen.blit(
                        image,
                        image.get_rect(
                            center=(
                                x + cell_size // 2,
                                y + cell_size // 2,
                            )
                        ),
                    )

        # Draw the moving player
        if current_position is not None:
            r, c = current_position

            center = (
                margin + c * cell_size + cell_size // 2,
                margin + r * cell_size + cell_size // 2,
            )

            pygame.draw.circle(
                screen,
                PLAYER_COLOR,
                center,
                max(5, cell_size // 4),
            )

        # Draw the control and inventory panel
        draw_text(
            "MAZE SOLVER",
            panel_x,
            margin,
            title_font,
        )

        draw_text(
            "KEY INVENTORY",
            panel_x,
            margin + 48,
            small_font,
        )

        inventory_y = margin + 77

        for key in "abcdef":
            pygame.draw.rect(
                screen,
                pair_colors[key],
                (panel_x, inventory_y, 22, 22),
            )

            status = (
                "Collected"
                if key in inventory
                else "Not collected"
            )

            draw_text(
                f"{key}: {status}",
                panel_x + 32,
                inventory_y + 2,
                small_font,
            )

            inventory_y += 30

        inventory_y += 12

        draw_text(
            f"Moves: {step} / {max(0, len(path) - 1)}",
            panel_x,
            inventory_y,
            small_font,
        )

        inventory_y += 30

        status = (
            "FINISHED"
            if finished
            else ("PAUSED" if paused else "PLAYING")
        )

        draw_text(
            f"Status: {status}",
            panel_x,
            inventory_y,
            small_font,
        )

        inventory_y += 35

        draw_text(
            "CONTROLS",
            panel_x,
            inventory_y,
            small_font,
        )

        inventory_y += 26

        controls = [
            "Space: Pause / resume",
            "Right: Advance one step",
            "R: Restart",
            "+ / -: Change speed",
            "Esc: Close",
        ]

        for control in controls:
            draw_text(
                control,
                panel_x,
                inventory_y,
                small_font,
                MUTED,
            )
            inventory_y += 24

        inventory_y += 12

        draw_text(
            f"Delay: {delay_ms} ms / move",
            panel_x,
            inventory_y,
            small_font,
        )

        pygame.display.flip()

    while running:
        elapsed = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE:
                    paused = not paused

                elif event.key == pygame.K_r:
                    step = 0
                    elapsed_ms = 0
                    paused = False
                    finished = len(path) <= 1

                elif event.key == pygame.K_RIGHT:
                    if path and step < len(path) - 1:
                        step += 1
                        elapsed_ms = 0
                        finished = step == len(path) - 1

                elif event.key in (
                    pygame.K_PLUS,
                    pygame.K_EQUALS,
                    pygame.K_KP_PLUS,
                ):
                    delay_ms = max(40, delay_ms - 40)

                elif event.key in (
                    pygame.K_MINUS,
                    pygame.K_KP_MINUS,
                ):
                    delay_ms = min(1000, delay_ms + 40)

        # Advance automatically unless paused or finished.
        if path and not paused and not finished:
            elapsed_ms += elapsed

            if elapsed_ms >= delay_ms:
                step += 1
                elapsed_ms = 0

                if step >= len(path) - 1:
                    step = len(path) - 1
                    finished = True

        draw_frame()

    pygame.quit()


if __name__ == "__main__":
    project_folder = Path(__file__).parent
    output_file = project_folder / "output" / "solved_maze.csv"

    print("=== MAZE SOLVER ===")
    print("1. Load maze from CSV")
    print("2. Generate a random maze")

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        maze_file = input(
            "Enter CSV filename (press Enter for maze.csv): "
        ).strip()

        if not maze_file:
            maze_file = "maze.csv"

        maze_path = Path(maze_file)

        if not maze_path.is_absolute():
            maze_path = project_folder / maze_path

        maze, start, exit_position = load_maze(maze_path)

    elif choice == "2":
        try:
            n = int(input("Enter maze size (odd number, at least 7): "))
            t = int(input("Enter number of key types (1 to 6): "))

            maze, start, exit_position = generate_maze(
                n=n,
                key_count=t
            )

            print("\nGenerated maze:")

            for row in maze:
                print(" ".join(row))

        except ValueError as error:
            print("Invalid input:", error)
            raise SystemExit(1)

    else:
        print("Invalid choice. Enter 1 or 2.")
        raise SystemExit(1)

    # Solve the selected maze
    distance, path = solve_maze(maze, start, exit_position)

    if distance == -1:
        print("\nShortest path length: -1")
        print("No valid path exists.")
    else:
        print("\nShortest path length:", distance)
        print("Path coordinates:", path)

        save_solution_csv(maze, path, output_file)
    visualize_maze(maze, path)