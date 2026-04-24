"""
generator.py
Generador automático de laberintos usando el algoritmo "Recursive Backtracker"
(DFS con backtracking).

Nota pedagógica: Este generador usa el MISMO algoritmo DFS que implementamos
para resolver laberintos, pero aplicado de forma inversa:
    - Resolver: explora celdas libres para encontrar la meta.
    - Generar:  "explora" paredes para convertirlas en celdas libres.

El laberinto resultante es "perfecto": existe exactamente un camino entre
cualquier par de celdas, sin ciclos ni áreas inaccesibles.

Complejidad:
    - Temporal: O(N) donde N es el número total de celdas en el grid.
    - Espacial: O(N) por la pila y el set de visitados.
"""

import random
from typing import Optional, Tuple, List
from .maze import Maze, WALL, FREE, START, END


def generate_maze(
    rows: int,
    cols: int,
    seed: Optional[int] = None,
    start: Optional[Tuple[int, int]] = None,
    end: Optional[Tuple[int, int]] = None,
) -> Maze:
    """
    Genera un laberinto aleatorio usando DFS con backtracking.

    Args:
        rows: filas del grid final. DEBE ser impar (ver nota).
        cols: columnas del grid final. DEBE ser impar.
        seed: semilla para reproducibilidad. None = aleatorio.
        start: posición del inicio. Por defecto (1, 1).
        end: posición de la meta. Por defecto (rows-2, cols-2).

    Returns:
        Objeto Maze listo para usar con bfs() o dfs().

    Raises:
        ValueError: si rows o cols no son impares o son menores a 3.

    Nota sobre dimensiones impares:
        El algoritmo piensa el grid como una cuadrícula de celdas separadas
        por paredes. Las celdas están en posiciones impares (1, 3, 5, ...)
        y las paredes en posiciones pares. Por eso las dimensiones deben ser
        impares: para que haya paredes en todos los bordes.
    """
    # --- Validaciones ---
    if rows < 3 or cols < 3:
        raise ValueError("Las dimensiones mínimas son 3x3.")
    if rows % 2 == 0 or cols % 2 == 0:
        raise ValueError(
            f"rows y cols deben ser impares. Recibidos: {rows}x{cols}. "
            f"Prueba con {rows if rows % 2 else rows + 1}x{cols if cols % 2 else cols + 1}."
        )

    # Inicializar generador aleatorio (reproducibilidad si hay seed)
    rng = random.Random(seed)

    # --- Inicializar grid lleno de paredes ---
    grid: List[List[int]] = [[WALL for _ in range(cols)] for _ in range(rows)]

    # --- Configurar inicio y meta ---
    # Deben estar en posiciones impares para que caigan en "celdas" del grid
    if start is None:
        start = (1, 1)
    if end is None:
        end = (rows - 2, cols - 2)

    _validate_cell_position(start, rows, cols, "start")
    _validate_cell_position(end, rows, cols, "end")

    # --- Algoritmo Recursive Backtracker ---
    # La celda actual siempre está en coordenadas impares.
    # Los movimientos son "de a dos" para saltar por encima de las paredes.
    DIRECTIONS_2X = [(-2, 0), (2, 0), (0, -2), (0, 2)]  # arriba, abajo, izq, der

    # Empezamos marcando la celda de inicio como libre
    stack: List[Tuple[int, int]] = [start]
    grid[start[0]][start[1]] = FREE
    visited: set = {start}

    while stack:
        current = stack[-1]  # miramos el tope sin sacarlo aún
        r, c = current

        # Buscar vecinos válidos (a distancia 2, aún no visitados)
        unvisited_neighbors = []
        for dr, dc in DIRECTIONS_2X:
            nr, nc = r + dr, c + dc
            # Debe estar dentro de límites (con margen para las paredes exteriores)
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1:
                if (nr, nc) not in visited:
                    unvisited_neighbors.append((nr, nc))

        if unvisited_neighbors:
            # Elegir un vecino al azar
            next_cell = rng.choice(unvisited_neighbors)
            nr, nc = next_cell

            # Derribar la pared INTERMEDIA entre la celda actual y la vecina
            # La pared está a distancia 1, en el mismo eje que el movimiento
            wall_r = (r + nr) // 2
            wall_c = (c + nc) // 2
            grid[wall_r][wall_c] = FREE

            # Marcar la celda vecina como libre y visitada
            grid[nr][nc] = FREE
            visited.add(next_cell)

            # Avanzar a la celda vecina
            stack.append(next_cell)
        else:
            # No hay vecinos disponibles → retroceder (backtrack)
            stack.pop()

    # --- Colocar inicio y meta ---
    grid[start[0]][start[1]] = START
    grid[end[0]][end[1]] = END

    return Maze(grid)


def _validate_cell_position(cell: Tuple[int, int], rows: int, cols: int, name: str) -> None:
    """Valida que una celda esté en posición impar (donde pueden estar las celdas libres)."""
    r, c = cell
    if not (1 <= r < rows - 1 and 1 <= c < cols - 1):
        raise ValueError(f"{name} {cell} está fuera de los límites válidos.")
    if r % 2 == 0 or c % 2 == 0:
        raise ValueError(
            f"{name} {cell} debe estar en coordenadas impares "
            f"(las celdas transitables están en posiciones impares del grid)."
        )


def generate_open_maze(rows: int, cols: int) -> Maze:
    """
    Genera un laberinto completamente abierto (sin paredes interiores).
    Útil para pruebas donde queremos ver diferencias grandes entre BFS y DFS.

    Args:
        rows, cols: dimensiones (no requieren ser impares).
    """
    grid = [[FREE for _ in range(cols)] for _ in range(rows)]
    grid[0][0] = START
    grid[rows - 1][cols - 1] = END
    return Maze(grid)


def generate_maze_with_loops(
    rows: int,
    cols: int,
    seed: Optional[int] = None,
    extra_openings: float = 0.1,
) -> Maze:
    """
    Genera un laberinto "imperfecto" con ciclos (múltiples caminos posibles).
    Empieza con un laberinto perfecto y luego derriba paredes adicionales.
    Esto es interesante porque BFS y DFS darán resultados MÁS diferentes.

    Args:
        rows, cols: dimensiones (deben ser impares).
        seed: semilla para reproducibilidad.
        extra_openings: fracción de paredes interiores a derribar (0.0 a 1.0).
                        0.1 = derriba el 10% de las paredes internas.
    """
    if not 0.0 <= extra_openings <= 1.0:
        raise ValueError("extra_openings debe estar entre 0.0 y 1.0")

    maze = generate_maze(rows, cols, seed)
    rng = random.Random(seed)

    # Identificar paredes internas candidatas a derribar
    # (paredes con celdas libres en lados opuestos)
    wall_candidates = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if maze.grid[r][c] == WALL:
                # Pared horizontal entre celdas verticales
                if (r > 0 and r < rows - 1 and
                    maze.grid[r - 1][c] == FREE and maze.grid[r + 1][c] == FREE):
                    wall_candidates.append((r, c))
                # Pared vertical entre celdas horizontales
                elif (c > 0 and c < cols - 1 and
                      maze.grid[r][c - 1] == FREE and maze.grid[r][c + 1] == FREE):
                    wall_candidates.append((r, c))

    # Derribar una fracción de esas paredes
    num_to_open = int(len(wall_candidates) * extra_openings)
    rng.shuffle(wall_candidates)
    for r, c in wall_candidates[:num_to_open]:
        maze.grid[r][c] = FREE

    return maze
