"""
Prueba rápida de la clase Maze.
Valida: construcción, vecinos, y representación visual.
"""

from maze.maze import Maze


# Laberinto de prueba 5x5
# S = inicio, █ = pared, . = libre, E = meta
test_grid = [
    [2, 0, 1, 0, 0],
    [1, 0, 1, 0, 1],
    [0, 0, 0, 0, 1],
    [0, 1, 1, 0, 0],
    [0, 0, 0, 1, 3],
]

maze = Maze(test_grid)

print("=" * 40)
print("LABERINTO DE PRUEBA")
print("=" * 40)
print(maze)
print()
print(f"Dimensiones: {maze.rows} filas x {maze.cols} columnas")
print(f"Inicio: {maze.start}")
print(f"Meta:   {maze.end}")
print()

# Probar vecinos de algunas celdas
print("=" * 40)
print("PRUEBA DE VECINOS")
print("=" * 40)

test_cells = [maze.start, (2, 2), (0, 4), maze.end]
for cell in test_cells:
    neighbors = maze.get_neighbors(cell)
    print(f"Vecinos de {cell}: {neighbors}")
