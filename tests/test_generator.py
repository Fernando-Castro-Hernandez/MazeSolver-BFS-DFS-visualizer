"""
Prueba del generador de laberintos.
Muestra los tres tipos de laberinto y cómo BFS/DFS se comportan en cada uno.
"""

from maze.generator import generate_maze, generate_open_maze, generate_maze_with_loops
from maze.bfs import bfs
from maze.dfs import dfs
from maze.metrics import measure_average


# Usamos la misma seed para que los laberintos sean reproducibles
SEED = 42


# ============================================================
# 1. Laberinto perfecto generado con DFS backtracker
# ============================================================
print("=" * 60)
print("1. LABERINTO PERFECTO (DFS backtracker)")
print("=" * 60)

perfect = generate_maze(rows=21, cols=21, seed=SEED)
print(perfect)
print()

bfs_r = measure_average(bfs, 5, perfect)
dfs_r = measure_average(dfs, 5, perfect)
print(f"BFS → camino: {bfs_r['path_length']:3} | visitados: {bfs_r['nodes_visited']:3} "
      f"| frontera máx: {bfs_r['max_frontier_size']:3} | tiempo: {bfs_r['avg_time_ms']:.3f} ms")
print(f"DFS → camino: {dfs_r['path_length']:3} | visitados: {dfs_r['nodes_visited']:3} "
      f"| frontera máx: {dfs_r['max_frontier_size']:3} | tiempo: {dfs_r['avg_time_ms']:.3f} ms")
print()
print("Observación: en un laberinto PERFECTO (sin ciclos), BFS y DFS")
print("encuentran el mismo camino (porque solo hay UN camino posible).")
print("La diferencia está en la cantidad de nodos visitados.")
print()


# ============================================================
# 2. Laberinto abierto (sin paredes interiores)
# ============================================================
print("=" * 60)
print("2. LABERINTO ABIERTO (sin paredes)")
print("=" * 60)

open_maze = generate_open_maze(rows=15, cols=15)
print(open_maze)
print()

bfs_r = measure_average(bfs, 5, open_maze)
dfs_r = measure_average(dfs, 5, open_maze)
print(f"BFS → camino: {bfs_r['path_length']:3} | visitados: {bfs_r['nodes_visited']:3} "
      f"| frontera máx: {bfs_r['max_frontier_size']:3} | tiempo: {bfs_r['avg_time_ms']:.3f} ms")
print(f"DFS → camino: {dfs_r['path_length']:3} | visitados: {dfs_r['nodes_visited']:3} "
      f"| frontera máx: {dfs_r['max_frontier_size']:3} | tiempo: {dfs_r['avg_time_ms']:.3f} ms")
print()
print("Observación: en un laberinto ABIERTO, hay MUCHOS caminos posibles.")
print("BFS encuentra el más corto; DFS tiende a recorrer casi todo el grid.")
print()


# ============================================================
# 3. Laberinto con ciclos (imperfecto)
# ============================================================
print("=" * 60)
print("3. LABERINTO CON CICLOS (10% paredes extra derribadas)")
print("=" * 60)

loopy = generate_maze_with_loops(rows=21, cols=21, seed=SEED, extra_openings=0.15)
print(loopy)
print()

bfs_r = measure_average(bfs, 5, loopy)
dfs_r = measure_average(dfs, 5, loopy)
print(f"BFS → camino: {bfs_r['path_length']:3} | visitados: {bfs_r['nodes_visited']:3} "
      f"| frontera máx: {bfs_r['max_frontier_size']:3} | tiempo: {bfs_r['avg_time_ms']:.3f} ms")
print(f"DFS → camino: {dfs_r['path_length']:3} | visitados: {dfs_r['nodes_visited']:3} "
      f"| frontera máx: {dfs_r['max_frontier_size']:3} | tiempo: {dfs_r['avg_time_ms']:.3f} ms")
print()
print("Observación: con ciclos, BFS y DFS pueden encontrar caminos DIFERENTES.")
print("Aquí se ve claramente la ventaja de BFS (camino más corto).")
print()


# ============================================================
# 4. Reproducibilidad: mismo seed → mismo laberinto
# ============================================================
print("=" * 60)
print("4. REPRODUCIBILIDAD (misma seed = mismo laberinto)")
print("=" * 60)

m1 = generate_maze(11, 11, seed=123)
m2 = generate_maze(11, 11, seed=123)
m3 = generate_maze(11, 11, seed=456)

print(f"¿m1 == m2 (misma seed)?   {m1.grid == m2.grid}")
print(f"¿m1 == m3 (distinta seed)? {m1.grid == m3.grid}")
print()
print("Laberinto con seed=123:")
print(m1)
print()
print("Laberinto con seed=456:")
print(m3)
