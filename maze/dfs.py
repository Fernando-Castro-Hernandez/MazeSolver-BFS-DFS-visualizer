"""
dfs.py
Implementación iterativa del algoritmo Depth-First Search (DFS)
para resolver laberintos, usando una pila explícita.

DFS explora el grafo en profundidad usando una pila (LIFO).
Encuentra un camino si existe, pero NO garantiza que sea el más corto.

¿Por qué la versión iterativa con pila en lugar de recursiva?
    1. Hace evidente el paralelo con BFS (solo cambia cola por pila).
    2. Evita stack overflow en laberintos muy grandes.
    3. Permite medir con precisión el uso de memoria (tamaño de la pila).

Complejidad temporal:  O(V + E)  — igual que BFS.
Complejidad espacial:  O(V)      por la pila, visited y parent.

Nota: Aunque la complejidad asintótica es la misma que BFS, en la práctica
el uso de memoria *promedio* suele ser menor en DFS (la pila rara vez
contiene todos los nodos simultáneamente).
"""

from typing import Tuple, Dict, List, Optional
from .maze import Maze


def dfs(maze: Maze) -> dict:
    """
    Ejecuta DFS iterativo sobre el laberinto desde maze.start hasta maze.end.

    Returns:
        dict con las mismas métricas que bfs() para permitir comparación directa:
            - algorithm: "DFS"
            - found: bool
            - path: lista de celdas desde inicio hasta meta
            - exploration_order: orden de visita
            - nodes_visited, path_length, max_frontier_size
    """
    start = maze.start
    end = maze.end

    # --- Estructuras auxiliares ---
    # Pila: una lista de Python funciona perfecto.
    # append() y pop() son O(1) al final de la lista.
    stack: List[Tuple[int, int]] = [start]

    # Set de visitados
    visited: set = {start}

    # Diccionario de padres para reconstruir el camino
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}

    # --- Métricas ---
    exploration_order: List[Tuple[int, int]] = []
    max_frontier_size = 1
    found = False

    # --- Bucle principal de DFS ---
    while stack:
        # Actualizamos la métrica de memoria
        if len(stack) > max_frontier_size:
            max_frontier_size = len(stack)

        # Sacamos el TOPE de la pila (LIFO = el más reciente)
        # Esta es LA ÚNICA diferencia real con BFS.
        current = stack.pop()
        exploration_order.append(current)

        # ¿Llegamos a la meta?
        if current == end:
            found = True
            break

        # Exploramos los vecinos
        for neighbor in maze.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)

    # --- Reconstruir el camino ---
    path = _reconstruct_path(parent, start, end) if found else []

    return {
        "algorithm": "DFS",
        "found": found,
        "path": path,
        "exploration_order": exploration_order,
        "nodes_visited": len(exploration_order),
        "path_length": len(path) - 1 if path else 0,
        "max_frontier_size": max_frontier_size,
    }


def _reconstruct_path(
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]],
    start: Tuple[int, int],
    end: Tuple[int, int],
) -> List[Tuple[int, int]]:
    """
    Reconstruye el camino desde 'start' hasta 'end' usando el diccionario
    de padres. Idéntico al de BFS.

    Nota: En el proyecto real podríamos factorizar esta función a un
    módulo compartido. La duplico aquí por claridad pedagógica.
    """
    path = []
    current: Optional[Tuple[int, int]] = end
    while current is not None:
        path.append(current)
        current = parent.get(current)
    path.reverse()
    return path
