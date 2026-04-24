"""
Prueba del módulo de métricas.
Incluye un experimento de escalabilidad: mide tiempo y memoria en laberintos
de distintos tamaños para validar experimentalmente la complejidad O(V).
"""

from maze.maze import Maze, WALL, FREE, START, END
from maze.bfs import bfs
from maze.dfs import dfs
from maze.metrics import measure, measure_average, format_metrics


# -------- PARTE 1: Medición en un laberinto concreto --------

test_grid = [
    [2, 0, 1, 0, 0],
    [1, 0, 1, 0, 1],
    [0, 0, 0, 0, 1],
    [0, 1, 1, 0, 0],
    [0, 0, 0, 1, 3],
]

maze = Maze(test_grid)

print("=" * 60)
print("MEDICIÓN INDIVIDUAL (laberinto 5x5)")
print("=" * 60)

bfs_result = measure(bfs, maze)
print(format_metrics(bfs_result))
print()
dfs_result = measure(dfs, maze)
print(format_metrics(dfs_result))
print()


# -------- PARTE 2: Mediciones promediadas (más confiables) --------

print("=" * 60)
print("MEDICIÓN PROMEDIADA (10 ejecuciones por algoritmo)")
print("=" * 60)

bfs_avg = measure_average(bfs, 10, maze)
print(format_metrics(bfs_avg))
print()
dfs_avg = measure_average(dfs, 10, maze)
print(format_metrics(dfs_avg))
print()


# -------- PARTE 3: Experimento de escalabilidad --------

def make_open_maze(n: int) -> Maze:
    """Crea un laberinto n x n completamente abierto (solo bordes como paredes no)."""
    grid = [[FREE for _ in range(n)] for _ in range(n)]
    grid[0][0] = START
    grid[n - 1][n - 1] = END
    return Maze(grid)


print("=" * 60)
print("EXPERIMENTO DE ESCALABILIDAD")
print("Laberintos abiertos de distintos tamaños (N x N)")
print("=" * 60)
print(f"{'N':>4} {'V':>8} {'BFS_ms':>10} {'DFS_ms':>10} "
      f"{'BFS_mem_KB':>12} {'DFS_mem_KB':>12} {'BFS_path':>10} {'DFS_path':>10}")
print("-" * 80)

for n in [10, 20, 40, 80, 160]:
    m = make_open_maze(n)
    v = n * n  # número de celdas transitables

    bfs_m = measure_average(bfs, 5, m)
    dfs_m = measure_average(dfs, 5, m)

    print(f"{n:>4} {v:>8} "
          f"{bfs_m['avg_time_ms']:>10.3f} {dfs_m['avg_time_ms']:>10.3f} "
          f"{bfs_m['peak_memory_kb']:>12.2f} {dfs_m['peak_memory_kb']:>12.2f} "
          f"{bfs_m['path_length']:>10} {dfs_m['path_length']:>10}")

print()
print("OBSERVACIONES ESPERADAS:")
print(" - El tiempo debería crecer aproximadamente lineal con V (O(V)).")
print(" - Si V se multiplica por 4 (N se duplica), el tiempo debería")
print("   multiplicarse por ~4 también.")
print(" - BFS siempre da el camino más corto (2*(N-1) en grid abierto).")
print(" - DFS puede dar un camino mucho más largo, a veces ~N^2.")
