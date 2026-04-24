"""
app.py
Servidor Flask que expone el backend de algoritmos de laberintos como una API REST.

Endpoints:
    POST /api/generate  → genera un laberinto aleatorio
    POST /api/solve     → resuelve un laberinto con BFS o DFS
    POST /api/compare   → resuelve con ambos algoritmos y devuelve ambos resultados
    GET  /api/health    → verifica que el servidor esté corriendo

Ejecución:
    python app.py
    → servidor corriendo en http://localhost:5000
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from maze.maze import Maze
from maze.bfs import bfs
from maze.dfs import dfs
from maze.metrics import measure
from maze.generator import generate_maze, generate_open_maze, generate_maze_with_loops


# --- Inicialización de Flask ---
# template_folder y static_folder son los defaults, los dejamos explícitos
# para que quede claro dónde busca cada cosa.
app = Flask(__name__, template_folder='templates', static_folder='static')

# Habilita CORS para que el frontend pueda llamar a la API.
# Como ahora Flask sirve todo desde el mismo origen, CORS no es estrictamente
# necesario, pero lo dejamos por si en algún momento se sirve el frontend
# desde otro lugar (por ejemplo un Live Server de VS Code).
CORS(app)


# --- Ruta principal: sirve el frontend ---
@app.route('/')
def index():
    """Sirve la página principal del frontend."""
    return render_template('index.html')


# =============================================================================
# HELPERS
# =============================================================================

def _maze_from_grid(grid_data) -> Maze:
    """
    Construye un objeto Maze a partir del grid recibido en el JSON.
    Incluye validación mínima y convierte a tipos nativos de Python.
    """
    if not isinstance(grid_data, list) or not grid_data:
        raise ValueError("El campo 'grid' debe ser una matriz no vacía.")

    # Aseguramos que cada valor sea entero (por si llega como string)
    grid = [[int(cell) for cell in row] for row in grid_data]
    return Maze(grid)


def _serialize_result(result: dict) -> dict:
    """
    Prepara un resultado de bfs/dfs/measure para enviar como JSON.
    Convierte tuplas a listas porque JSON no tiene tuplas.
    """
    return {
        "algorithm": result["algorithm"],
        "found": result["found"],
        # Convertir tuplas (fila, col) a listas [fila, col]
        "path": [list(cell) for cell in result["path"]],
        "exploration_order": [list(cell) for cell in result["exploration_order"]],
        "nodes_visited": result["nodes_visited"],
        "path_length": result["path_length"],
        "max_frontier_size": result["max_frontier_size"],
        # Métricas físicas (añadidas por measure)
        "execution_time_ms": round(result.get("execution_time_ms", 0), 4),
        "execution_time_us": round(result.get("execution_time_us", 0), 2),
        "peak_memory_bytes": result.get("peak_memory_bytes", 0),
        "peak_memory_kb": round(result.get("peak_memory_kb", 0), 3),
    }


def _serialize_maze(maze: Maze) -> dict:
    """Serializa un Maze para enviar como respuesta JSON."""
    return {
        "grid": maze.grid,
        "rows": maze.rows,
        "cols": maze.cols,
        "start": list(maze.start),
        "end": list(maze.end),
    }


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.route("/api/health", methods=["GET"])
def health():
    """Endpoint de verificación. Útil para el frontend al iniciar."""
    return jsonify({"status": "ok", "message": "Maze API is running"})


@app.route("/api/generate", methods=["POST"])
def generate():
    """
    Genera un laberinto aleatorio.

    Request JSON:
        rows (int):    filas (debe ser impar para perfect/loopy, mín 3)
        cols (int):    columnas (mismo requisito)
        type (str):    "perfect" | "open" | "loopy" (opcional, default "perfect")
        seed (int):    semilla opcional para reproducibilidad
        extra_openings (float): solo para type="loopy", default 0.1
    """
    try:
        data = request.get_json() or {}
        rows = int(data.get("rows", 21))
        cols = int(data.get("cols", 21))
        maze_type = data.get("type", "perfect")
        seed = data.get("seed")
        if seed is not None:
            seed = int(seed)

        if maze_type == "perfect":
            maze = generate_maze(rows, cols, seed=seed)
        elif maze_type == "open":
            maze = generate_open_maze(rows, cols)
        elif maze_type == "loopy":
            extra = float(data.get("extra_openings", 0.1))
            maze = generate_maze_with_loops(rows, cols, seed=seed, extra_openings=extra)
        else:
            return jsonify({"error": f"Tipo de laberinto desconocido: {maze_type}"}), 400

        return jsonify(_serialize_maze(maze))

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@app.route("/api/solve", methods=["POST"])
def solve():
    """
    Resuelve un laberinto usando BFS o DFS.

    Request JSON:
        grid (list[list[int]]): matriz del laberinto
        algorithm (str):        "bfs" o "dfs"
    """
    try:
        data = request.get_json() or {}
        if "grid" not in data:
            return jsonify({"error": "Falta el campo 'grid'"}), 400

        algorithm = data.get("algorithm", "bfs").lower()
        if algorithm not in ("bfs", "dfs"):
            return jsonify({"error": "algorithm debe ser 'bfs' o 'dfs'"}), 400

        maze = _maze_from_grid(data["grid"])
        algo_fn = bfs if algorithm == "bfs" else dfs
        result = measure(algo_fn, maze)

        return jsonify(_serialize_result(result))

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@app.route("/api/compare", methods=["POST"])
def compare():
    """
    Resuelve un laberinto con ambos algoritmos y devuelve ambos resultados.
    Útil para visualización lado a lado.

    Request JSON:
        grid (list[list[int]]): matriz del laberinto
    """
    try:
        data = request.get_json() or {}
        if "grid" not in data:
            return jsonify({"error": "Falta el campo 'grid'"}), 400

        maze = _maze_from_grid(data["grid"])

        bfs_result = measure(bfs, maze)
        # Nota: construimos un maze "fresco" para DFS para que la medición
        # de memoria no incluya las estructuras que BFS dejó en memoria.
        dfs_result = measure(dfs, maze)

        return jsonify({
            "bfs": _serialize_result(bfs_result),
            "dfs": _serialize_result(dfs_result),
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# =============================================================================
# MANEJO DE ERRORES GLOBALES
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Método HTTP no permitido para este endpoint"}), 405


# =============================================================================
# ARRANQUE DEL SERVIDOR
# =============================================================================

if __name__ == "__main__":
    # debug=True recarga automáticamente al cambiar el código
    # host=0.0.0.0 permite acceso desde otras máquinas en la red local
    app.run(debug=True, host="0.0.0.0", port=5000)
