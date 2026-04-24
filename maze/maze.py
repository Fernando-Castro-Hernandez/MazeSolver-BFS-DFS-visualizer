"""
maze.py
Representación de un laberinto como matriz 2D.

Valores en el grid:
    0 = celda libre (transitable)
    1 = pared (no transitable)
    2 = inicio (start)
    3 = meta (end)

Coordenadas: (fila, columna) — consistente con la indexación de listas en Python.
"""

from typing import List, Tuple, Optional


# Desplazamientos para obtener vecinos en 4 direcciones
# (arriba, abajo, izquierda, derecha)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Constantes para los valores del grid (mejor que usar números "mágicos")
FREE = 0
WALL = 1
START = 2
END = 3


class Maze:
    """
    Representa un laberinto como una matriz 2D.
    El grafo está implícito: los vecinos de una celda son las 4 celdas
    adyacentes (arriba, abajo, izquierda, derecha) que no sean paredes.
    """

    def __init__(self, grid: List[List[int]]):
        """
        Inicializa el laberinto a partir de una matriz 2D.

        Args:
            grid: Lista de listas de enteros. Debe contener exactamente
                  un inicio (2) y una meta (3).

        Raises:
            ValueError: Si el grid está vacío, no es rectangular, o no tiene
                        exactamente un inicio y una meta.
        """
        # Validaciones básicas
        if not grid or not grid[0]:
            raise ValueError("El grid no puede estar vacío.")

        self.rows = len(grid)
        self.cols = len(grid[0])

        # Verificar que todas las filas tengan la misma longitud
        if any(len(row) != self.cols for row in grid):
            raise ValueError("Todas las filas deben tener la misma longitud.")

        # Guardar el grid (hacemos una copia para evitar mutaciones externas)
        self.grid = [row[:] for row in grid]

        # Encontrar y guardar el inicio y la meta
        self.start = self._find_cell(START)
        self.end = self._find_cell(END)

        if self.start is None:
            raise ValueError("El laberinto debe tener un punto de inicio (valor 2).")
        if self.end is None:
            raise ValueError("El laberinto debe tener una meta (valor 3).")

    def _find_cell(self, value: int) -> Optional[Tuple[int, int]]:
        """
        Busca la primera celda con el valor dado.
        Método privado (por convención, con guion bajo al inicio).

        Returns:
            Tupla (fila, columna) o None si no se encuentra.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == value:
                    return (r, c)
        return None

    def in_bounds(self, cell: Tuple[int, int]) -> bool:
        """Verifica si una celda está dentro de los límites del grid."""
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_walkable(self, cell: Tuple[int, int]) -> bool:
        """
        Verifica si una celda es transitable (no es pared y está en rango).
        El inicio y la meta también son transitables.
        """
        if not self.in_bounds(cell):
            return False
        r, c = cell
        return self.grid[r][c] != WALL

    def get_neighbors(self, cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Devuelve las celdas vecinas transitables de una celda dada.
        Este es el corazón del grafo implícito: define qué celdas están
        "conectadas" con cuál.

        Complejidad: O(1) — siempre revisa 4 vecinos.
        """
        r, c = cell
        neighbors = []
        for dr, dc in DIRECTIONS:
            neighbor = (r + dr, c + dc)
            if self.is_walkable(neighbor):
                neighbors.append(neighbor)
        return neighbors

    def __str__(self) -> str:
        """
        Representación visual del laberinto para imprimir en consola.
        Útil para depurar antes de tener la interfaz gráfica.
        """
        symbols = {
            FREE: ".",
            WALL: "█",
            START: "S",
            END: "E",
        }
        lines = []
        for row in self.grid:
            line = " ".join(symbols.get(cell, "?") for cell in row)
            lines.append(line)
        return "\n".join(lines)

    def copy(self) -> "Maze":
        """Devuelve una copia independiente del laberinto."""
        return Maze([row[:] for row in self.grid])
