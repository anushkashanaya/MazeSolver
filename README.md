
# MazeSolver 🧩

A Python-based maze solver that uses Breadth-First Search (BFS) to find the shortest path through a maze containing walls, keys, and locked doors.

## Features
- Solve mazes using BFS.
- Generate random mazes with 1–6 key-door pairs.
- Load mazes from CSV files.
- Save solved mazes with the path marked as `x`.
- Visualize maze solving with Pygame.
- Animate player movement, key collection, and door unlocking.

## Technologies Used
- Python
- Pygame
- CSV
- Breadth-First Search (BFS)

## How to Run

Install Python 3 and Pygame, then run:

```bash
python -m pip install pygame
python main.py
```

Follow the terminal prompts to load a CSV maze or generate a random maze.

## Maze Symbols
- `S` — Start
- `X` — Exit (displayed as E in the visualization)
- `#` — Wall
- `.` — Open path
- `a`–`f` — Keys
- `A`–`F` — Locked doors
- `x` — Solved path in the output CSV

## Controls
- Space — Pause or resume
- Right Arrow — Advance one step
- R — Restart
- `+` / `-` — Adjust speed
- Esc — Close visualization

