# Maze BFS vs DFS Visualizer

> Interactive web-based maze solver comparing **Breadth-First Search** and **Depth-First Search** side by side. Educational project focused on demonstrating how the choice of data structure (queue vs stack) determines algorithmic behavior.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?logo=javascript&logoColor=black)


---

## About

This project was built for the *Data Structures* course at **Instituto Tecnológico de Software** as the final evaluation of the subject. It explores one of the most elegant demonstrations in computer science: how two algorithms with nearly identical code can produce dramatically different results based solely on their underlying data structure.

The project implements both **BFS** (using a queue) and **DFS** (using a stack) to solve mazes, visualizes their exploration step-by-step in real time, and measures their performance across four dimensions: path length, exploration order, memory usage, and execution time.

**Key insight:** the only real difference between the two algorithms is `queue.popleft()` versus `stack.pop()` — a single line of code. Yet this one change transforms an algorithm that *guarantees* the shortest path into one that *does not*.

---

## Features

- **Three maze types:** perfect (single path), loopy (multiple paths), and open (no walls).
- **Interactive editor:** click and drag to draw walls, place start and end points with the mouse.
- **Two visualization modes:**
  - *Instant* — shows final result immediately.
  - *Animated* — step-by-step exploration with adjustable speed.
- **Side-by-side comparison:** both algorithms run on the same maze, rendered in parallel.
- **Real-time metrics:** path length, nodes visited, maximum frontier size, execution time (`time.perf_counter()`), and peak memory usage (`tracemalloc`).
- **Automatic maze generation:** DFS-with-backtracking for perfect mazes, with configurable size and seed for reproducibility.

---

## Tech Stack

**Backend**
- Python 3.10+
- Flask (REST API)
- flask-cors
- `collections.deque` (BFS queue)
- `tracemalloc` (memory profiling)
- `time.perf_counter()` (high-precision timing)

**Frontend**
- Vanilla JavaScript (ES modules)
- HTML5 Canvas
- CSS with custom properties (no frameworks)
- Custom typography (Fraunces + JetBrains Mono)

No build step, no transpilation, no bundler. The project runs with a single `python app.py` command.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│               Frontend (browser)                │
│  HTML + Canvas + vanilla JS ES modules          │
│  - Render two mazes side by side                │
│  - Editor: click/drag to mark start/end/walls   │
│  - Animate exploration step-by-step             │
└─────────────────┬───────────────────────────────┘
                  │  HTTP (JSON)
                  ↓
┌─────────────────────────────────────────────────┐
│         Backend (Python + Flask)                │
│  ┌───────────────────────────────────────────┐  │
│  │  REST API (4 endpoints)                   │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │  Algorithm layer                          │  │
│  │  - Maze (2D matrix, implicit graph)       │  │
│  │  - BFS (deque-based)                      │  │
│  │  - DFS (iterative, explicit stack)        │  │
│  │  - Metrics wrapper (time + memory)        │  │
│  │  - Maze generator (3 variants)            │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Installation

Requires Python 3.10 or higher.

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/MazeSolver-BFS-DFS-visualizer.git
cd MazeSolver-BFS-DFS-visualizer

# (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Open your browser at **http://localhost:5000**.

---

## Usage

1. **Generate a maze:** choose the type (perfect, loopy, open) and size, then click *Generar*.
2. **Edit manually:** select a tool (wall, erase, start, end) and click/drag on either maze. Changes are synchronized between both panels.
3. **Choose visualization mode:** *Instantáneo* for immediate results, *Animado* for step-by-step exploration.
4. **Solve:** click *Resolver*. Both algorithms run in parallel and metrics appear in the comparison table below.

---

## API Reference

All endpoints return JSON. The frontend consumes them, but you can also test with `curl` or Postman.

### `GET /api/health`
Health check. Returns `{ "status": "ok", "message": "Maze API is running" }`.

### `POST /api/generate`
Generates a random maze.

```json
{
  "rows": 21,
  "cols": 21,
  "type": "perfect",
  "seed": 42
}
```

Types: `perfect`, `open`, `loopy`. For `loopy`, an optional `extra_openings` field (0.0 to 1.0) controls how many extra walls are knocked down.

### `POST /api/solve`
Solves a maze with a single algorithm.

```json
{
  "grid": [[2, 0, 1], [0, 0, 0], [1, 0, 3]],
  "algorithm": "bfs"
}
```

Returns path, exploration order, and all metrics.

### `POST /api/compare`
Runs both algorithms on the same grid and returns both results in one response. This is what the frontend uses for side-by-side comparison.

---

## Project Structure

```
maze-bfs-dfs-visualizer/
├── app.py                  # Flask server (API + serves frontend)
├── requirements.txt
├── README.md
│
├── maze/                   # Backend logic
│   ├── maze.py             # Maze class (2D matrix, implicit graph)
│   ├── bfs.py              # BFS with deque
│   ├── dfs.py              # Iterative DFS with explicit stack
│   ├── metrics.py          # Time and memory measurement
│   └── generator.py        # Maze generator (3 variants)
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/styles.css
│   └── js/
│       ├── api.js          # API wrapper
│       ├── maze-canvas.js  # Canvas rendering class
│       ├── editor.js       # Cursor interaction
│       ├── animator.js     # Step-by-step animation
│       └── main.js         # Entry point
│
└── tests/                  # Test scripts for each module
```

---


## Authors

- **Fernando** — Mérida, Yucatán
- **Venus**
- **Eruviel**

*Data Structures · Evaluation 2 · Final Project*
*Instituto Tecnológico de Software*
---


