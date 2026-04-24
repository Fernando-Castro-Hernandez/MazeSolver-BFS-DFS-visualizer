"""
Prueba con un laberinto ABIERTO (pocas paredes).
Aquí se ve claramente cómo BFS y DFS se comportan de forma distinta.
"""

from maze.maze import Maze, WALL, FREE, START, END
from maze.bfs import bfs
from maze.dfs import dfs


# Laberinto 8x8 muy abierto: solo algunas paredes
open_grid = [
    [2, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 3],
]

maze = Maze(open_grid)
bfs_r = bfs(maze)
dfs_r = dfs(maze)


def render(maze, path, explored):
    symbols = {FREE: ".", WALL: "█", START: "S", END: "E"}
    path_set = set(path) - {maze.start, maze.end}
    explored_set = set(explored) - path_set - {maze.start, maze.end}
    lines = []
    for r, row in enumerate(maze.grid):
        chars = []
        for c, cell in enumerate(row):
            if (r, c) in path_set:
                chars.append("*")
            elif (r, c) in explored_set:
                chars.append("o")
            else:
                chars.append(symbols.get(cell, "?"))
        lines.append(" ".join(chars))
    return "\n".join(lines)


print("LABERINTO 8x8 (abierto, con pasillos en zigzag)")
print(maze)
print()
print("=" * 50)
print("BFS")
print("=" * 50)
print(render(maze, bfs_r["path"], bfs_r["exploration_order"]))
print(f"  Camino: {bfs_r['path_length']} pasos | Visitados: {bfs_r['nodes_visited']} | Frontera máx: {bfs_r['max_frontier_size']}")
print()
print("=" * 50)
print("DFS")
print("=" * 50)
print(render(maze, dfs_r["path"], dfs_r["exploration_order"]))
print(f"  Camino: {dfs_r['path_length']} pasos | Visitados: {dfs_r['nodes_visited']} | Frontera máx: {dfs_r['max_frontier_size']}")
print()

print("=" * 50)
print("DIFERENCIAS OBSERVADAS")
print("=" * 50)
print(f"Diferencia en longitud del camino: {dfs_r['path_length'] - bfs_r['path_length']} pasos (DFS extra)")
print(f"Diferencia en nodos visitados:     {dfs_r['nodes_visited'] - bfs_r['nodes_visited']} nodos")
print(f"Diferencia en frontera máxima:     {dfs_r['max_frontier_size'] - bfs_r['max_frontier_size']}")
