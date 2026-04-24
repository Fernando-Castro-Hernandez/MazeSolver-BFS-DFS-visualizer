"""
bfs.py
Implementación del algoritmo Breadth-First Search (BFS)
para resolver laberintos.

BFS explora el grafo por niveles usando una cola (FIFO).
Garantiza encontrar el camino más corto en grafos no ponderados.

Complejidad temporal:  O(V + E)  donde V = celdas, E = conexiones.
Complejidad espacial:  O(V)      por la cola, visited y parent.

En un grid rectangular de filas*cols celdas:
    - V = filas * cols (en el peor caso, sin paredes)
    - E ≤ 4V (cada celda tiene a lo mucho 4 vecinos)
    - Por lo tanto, BFS es O(V) = O(filas * cols).
"""

from collections import deque
from typing import Tuple, Dict, List, Optional
from .maze import Maze


def bfs(maze: Maze) -> dict:
    """
    Ejecuta BFS sobre el laberinto desde maze.start hasta maze.end.

    Returns:
        dict con las métricas y el resultado de la búsqueda:
            - algorithm: "BFS"
            - found: bool, si se encontró un camino
            - path: lista de celdas (fila, col) desde inicio hasta meta
            - exploration_order: lista de celdas en el orden en que se visitaron
                                 (útil para animar en el frontend)
            - nodes_visited: total de nodos visitados
            - path_length: longitud del camino (número de pasos)
            - max_frontier_size: tamaño máximo que alcanzó la cola
                                 (aproximación del uso de memoria)
    """
    start = maze.start
    end = maze.end

    # --- Estructuras auxiliares ---
    # Cola: usamos deque porque tiene append() y popleft() en O(1).
    # Una lista con pop(0) sería O(n) y arruinaría la complejidad.
    queue: deque = deque()
    queue.append(start)

    # Set de visitados: búsqueda en O(1) promedio.
    # Usamos un set en lugar de una matriz booleana por simplicidad.
    visited: set = {start}

    # Diccionario de padres para reconstruir el camino.
    # parent[nodo] = nodo desde el cual llegamos por primera vez a "nodo".
    # El inicio no tiene padre (None).
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}

    # --- Métricas ---
    exploration_order: List[Tuple[int, int]] = []
    max_frontier_size = 1  # La cola empieza con 1 elemento (el inicio)
    found = False

    # --- Bucle principal de BFS ---
    while queue:
        # Actualizamos la métrica de memoria antes de sacar el siguiente nodo
        if len(queue) > max_frontier_size:
            max_frontier_size = len(queue)

        # Sacamos el primer nodo de la cola (FIFO = el más antiguo)
        current = queue.popleft()
        exploration_order.append(current)

        # ¿Llegamos a la meta? Terminamos la búsqueda.
        if current == end:
            found = True
            break

        # Exploramos los vecinos
        for neighbor in maze.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)           # Marcamos como visitado
                parent[neighbor] = current      # Recordamos de dónde venimos
                queue.append(neighbor)          # Lo encolamos para procesarlo

    # --- Reconstruir el camino ---
    path = _reconstruct_path(parent, start, end) if found else []

    return {
        "algorithm": "BFS",
        "found": found,
        "path": path,
        "exploration_order": exploration_order,
        "nodes_visited": len(exploration_order),
        "path_length": len(path) - 1 if path else 0,  # número de pasos = nodos - 1
        "max_frontier_size": max_frontier_size,
    }


def _reconstruct_path(
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]],
    start: Tuple[int, int],
    end: Tuple[int, int],
) -> List[Tuple[int, int]]:
    """
    Reconstruye el camino desde 'start' hasta 'end' usando el diccionario
    de padres. Empezamos en 'end' y vamos hacia atrás siguiendo los padres
    hasta llegar a 'start'. Luego invertimos la lista.

    Complejidad: O(longitud del camino)
    """
    path = []
    current: Optional[Tuple[int, int]] = end
    while current is not None:
        path.append(current)
        current = parent.get(current)
    path.reverse()  # Estaba de end→start, lo volteamos a start→end
    return path
