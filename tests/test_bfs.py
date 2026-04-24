"""
Prueba del algoritmo BFS.
Muestra el camino encontrado y el orden de exploración visualmente.
"""

from maze.maze import Maze, WALL, FREE, START, END
from maze.bfs import bfs


# Mismo laberinto 5x5 que usamos antes
test_grid = [
    [2, 0, 1, 0, 0],
    [1, 0, 1, 0, 1],
    [0, 0, 0, 0, 1],
    [0, 1, 1, 0, 0],
    [0, 0, 0, 1, 3],
]

maze = Maze(test_grid)

print("=" * 50)
print("LABERINTO ORIGINAL")
print("=" * 50)
print(maze)
print()

# Ejecutar BFS
result = bfs(maze)

print("=" * 50)
print(f"RESULTADO {result['algorithm']}")
print("=" * 50)
print(f"¿Se encontró camino?   {result['found']}")
print(f"Longitud del camino:   {result['path_length']} pasos")
print(f"Nodos visitados:       {result['nodes_visited']}")
print(f"Tamaño máx. de cola:   {result['max_frontier_size']}")
print(f"Camino encontrado:     {result['path']}")
print()


def render_with_path(maze: Maze, result: dict) -> str:
    """Dibuja el laberinto marcando el camino encontrado con '*'."""
    symbols = {FREE: ".", WALL: "█", START: "S", END: "E"}
    path_set = set(result["path"]) - {maze.start, maze.end}
    lines = []
    for r, row in enumerate(maze.grid):
        chars = []
        for c, cell in enumerate(row):
            if (r, c) in path_set:
                chars.append("*")
            else:
                chars.append(symbols.get(cell, "?"))
        lines.append(" ".join(chars))
    return "\n".join(lines)


print("=" * 50)
print("CAMINO ENCONTRADO (marcado con *)")
print("=" * 50)
print(render_with_path(maze, result))
print()


def render_with_exploration(maze: Maze, result: dict) -> str:
    """Dibuja el laberinto marcando las celdas exploradas con 'o'."""
    symbols = {FREE: ".", WALL: "█", START: "S", END: "E"}
    explored_set = set(result["exploration_order"]) - {maze.start, maze.end}
    lines = []
    for r, row in enumerate(maze.grid):
        chars = []
        for c, cell in enumerate(row):
            if (r, c) in explored_set:
                chars.append("o")
            else:
                chars.append(symbols.get(cell, "?"))
        lines.append(" ".join(chars))
    return "\n".join(lines)


print("=" * 50)
print("CELDAS EXPLORADAS (marcadas con o)")
print("=" * 50)
print(render_with_exploration(maze, result))
print()

print("=" * 50)
print("ORDEN DE EXPLORACIÓN (primeros 10 pasos)")
print("=" * 50)
for i, cell in enumerate(result["exploration_order"][:10]):
    print(f"  Paso {i+1}: visitó {cell}")
if len(result["exploration_order"]) > 10:
    print(f"  ... y {len(result['exploration_order']) - 10} más")
