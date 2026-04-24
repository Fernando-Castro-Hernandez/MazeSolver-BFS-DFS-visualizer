"""
Prueba comparativa: BFS vs DFS en el mismo laberinto.
Este es el preview de lo que será la comparación final del proyecto.
"""

from maze.maze import Maze, WALL, FREE, START, END
from maze.bfs import bfs
from maze.dfs import dfs


# Mismo laberinto 5x5 de los tests anteriores
test_grid = [
    [2, 0, 1, 0, 0],
    [1, 0, 1, 0, 1],
    [0, 0, 0, 0, 1],
    [0, 1, 1, 0, 0],
    [0, 0, 0, 1, 3],
]

maze = Maze(test_grid)

print("=" * 60)
print("LABERINTO DE PRUEBA")
print("=" * 60)
print(maze)
print()

# Ejecutar ambos algoritmos
bfs_result = bfs(maze)
dfs_result = dfs(maze)


def render_with_overlay(maze: Maze, path, explored) -> str:
    """
    Dibuja el laberinto con:
        * = celdas del camino final
        o = celdas exploradas (pero no en el camino)
    """
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


print("=" * 60)
print("BFS (* = camino final, o = explorado pero descartado)")
print("=" * 60)
print(render_with_overlay(maze, bfs_result["path"], bfs_result["exploration_order"]))
print()

print("=" * 60)
print("DFS (* = camino final, o = explorado pero descartado)")
print("=" * 60)
print(render_with_overlay(maze, dfs_result["path"], dfs_result["exploration_order"]))
print()

# Tabla comparativa
print("=" * 60)
print("COMPARACIÓN LADO A LADO")
print("=" * 60)
print(f"{'Métrica':<30} {'BFS':>12} {'DFS':>12}")
print("-" * 60)
print(f"{'Camino encontrado':<30} {str(bfs_result['found']):>12} {str(dfs_result['found']):>12}")
print(f"{'Longitud del camino':<30} {bfs_result['path_length']:>12} {dfs_result['path_length']:>12}")
print(f"{'Nodos visitados':<30} {bfs_result['nodes_visited']:>12} {dfs_result['nodes_visited']:>12}")
print(f"{'Tamaño máx. frontera':<30} {bfs_result['max_frontier_size']:>12} {dfs_result['max_frontier_size']:>12}")
print()

# Análisis de optimalidad
print("=" * 60)
print("ANÁLISIS DE OPTIMALIDAD")
print("=" * 60)
if bfs_result["path_length"] == dfs_result["path_length"]:
    print("En este laberinto, ambos algoritmos encontraron caminos de igual longitud.")
    print("Esto es coincidencia — DFS no GARANTIZA caminos óptimos.")
else:
    diff = dfs_result["path_length"] - bfs_result["path_length"]
    print(f"BFS encontró un camino {diff} pasos más corto que DFS.")
    print("Esto confirma que BFS es óptimo para grafos no ponderados,")
    print("mientras que DFS encuentra una solución sin garantizar optimalidad.")
