"""
Prueba de la API usando el test client de Flask.
Esto simula peticiones HTTP sin necesidad de levantar un servidor real.
Es la forma estándar de testear APIs Flask.
"""

import json
from app import app


client = app.test_client()


def pretty(response):
    """Imprime una respuesta JSON formateada, recortada si es muy larga."""
    data = response.get_json()
    # Recortar campos muy largos para que sea legible
    if isinstance(data, dict):
        for key in ("exploration_order", "path", "grid"):
            if key in data and isinstance(data[key], list) and len(data[key]) > 5:
                original_len = len(data[key])
                data[key] = data[key][:3] + [f"... ({original_len} items total)"]
        for algo_key in ("bfs", "dfs"):
            if algo_key in data and isinstance(data[algo_key], dict):
                for key in ("exploration_order", "path"):
                    if key in data[algo_key] and len(data[algo_key][key]) > 5:
                        original_len = len(data[algo_key][key])
                        data[algo_key][key] = data[algo_key][key][:3] + \
                            [f"... ({original_len} items total)"]
    return json.dumps(data, indent=2)


print("=" * 60)
print("TEST 1: GET /api/health")
print("=" * 60)
resp = client.get("/api/health")
print(f"Status: {resp.status_code}")
print(pretty(resp))
print()


print("=" * 60)
print("TEST 2: POST /api/generate (laberinto perfecto 11x11)")
print("=" * 60)
resp = client.post("/api/generate", json={
    "rows": 11,
    "cols": 11,
    "type": "perfect",
    "seed": 42
})
print(f"Status: {resp.status_code}")
print(pretty(resp))
print()


print("=" * 60)
print("TEST 3: POST /api/solve con BFS")
print("=" * 60)
# Usamos un grid pequeño para que la respuesta sea legible
grid = [
    [2, 0, 1, 0, 0],
    [1, 0, 1, 0, 1],
    [0, 0, 0, 0, 1],
    [0, 1, 1, 0, 0],
    [0, 0, 0, 1, 3],
]
resp = client.post("/api/solve", json={
    "grid": grid,
    "algorithm": "bfs"
})
print(f"Status: {resp.status_code}")
print(pretty(resp))
print()


print("=" * 60)
print("TEST 4: POST /api/solve con DFS")
print("=" * 60)
resp = client.post("/api/solve", json={
    "grid": grid,
    "algorithm": "dfs"
})
print(f"Status: {resp.status_code}")
print(pretty(resp))
print()


print("=" * 60)
print("TEST 5: POST /api/compare (ambos algoritmos a la vez)")
print("=" * 60)
resp = client.post("/api/compare", json={"grid": grid})
print(f"Status: {resp.status_code}")
print(pretty(resp))
print()


print("=" * 60)
print("TEST 6: Manejo de errores — grid inválido")
print("=" * 60)
resp = client.post("/api/solve", json={
    "grid": [[2, 0], [0, 0]],  # sin meta (3)
    "algorithm": "bfs"
})
print(f"Status: {resp.status_code}")
print(pretty(resp))
print()


print("=" * 60)
print("TEST 7: Manejo de errores — algoritmo inválido")
print("=" * 60)
resp = client.post("/api/solve", json={
    "grid": grid,
    "algorithm": "astar"
})
print(f"Status: {resp.status_code}")
print(pretty(resp))
print()


print("=" * 60)
print("TEST 8: Manejo de errores — endpoint inexistente")
print("=" * 60)
resp = client.get("/api/foo")
print(f"Status: {resp.status_code}")
print(pretty(resp))
print()


print("=" * 60)
print("TEST 9: Flujo completo — generar y resolver")
print("=" * 60)
# Paso A: generar un laberinto
gen_resp = client.post("/api/generate", json={
    "rows": 15, "cols": 15, "type": "loopy", "seed": 100, "extra_openings": 0.15
})
gen_data = gen_resp.get_json()
print(f"Laberinto generado: {gen_data['rows']}x{gen_data['cols']}, "
      f"start={gen_data['start']}, end={gen_data['end']}")

# Paso B: resolverlo con ambos algoritmos
comp_resp = client.post("/api/compare", json={"grid": gen_data["grid"]})
comp_data = comp_resp.get_json()
print(f"\nResultados comparativos:")
print(f"  BFS → camino: {comp_data['bfs']['path_length']:3} pasos | "
      f"visitados: {comp_data['bfs']['nodes_visited']:3} | "
      f"tiempo: {comp_data['bfs']['execution_time_ms']:.3f} ms")
print(f"  DFS → camino: {comp_data['dfs']['path_length']:3} pasos | "
      f"visitados: {comp_data['dfs']['nodes_visited']:3} | "
      f"tiempo: {comp_data['dfs']['execution_time_ms']:.3f} ms")
