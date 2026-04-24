# Laberintos: BFS vs DFS

Proyecto comparativo de los algoritmos Breadth-First Search y Depth-First Search aplicados a la resolución de laberintos. Frontend interactivo con edición visual, generación automática y animación paso a paso.

## Estructura

```
maze_project/
├── app.py                  # Servidor Flask (API + sirve el frontend)
├── requirements.txt
├── README.md
│
├── maze/                   # Backend — lógica de algoritmos
│   ├── maze.py             # Clase Maze (matriz 2D, grafo implícito)
│   ├── bfs.py              # BFS con cola (deque)
│   ├── dfs.py              # DFS iterativo con pila
│   ├── metrics.py          # Medición de tiempo y memoria
│   └── generator.py        # Generador de laberintos (3 tipos)
│
├── templates/
│   └── index.html          # Página principal del frontend
│
├── static/
│   ├── css/styles.css      # Estilos (tema editorial técnico)
│   └── js/
│       ├── api.js          # Wrapper de la API
│       ├── maze-canvas.js  # Clase MazeCanvas (dibujo en canvas)
│       ├── editor.js       # Edición con el cursor
│       ├── animator.js     # Animación paso a paso
│       └── main.js         # Orquestador principal
│
└── tests/                  # Scripts de prueba
```

## Instalación y ejecución

```bash
pip install -r requirements.txt
python app.py
```

Abre el navegador en `http://localhost:5000`.

## Cómo usar el frontend

1. **Generar un laberinto:** elige tipo (perfecto, con ciclos, abierto) y tamaño, presiona "Generar".
2. **Editar:** selecciona una herramienta (pared, borrar, inicio, meta) y haz click/drag en cualquiera de los dos laberintos. Los cambios se reflejan en ambos automáticamente.
3. **Elegir modo:** instantáneo (resultado directo) o animado (exploración paso a paso).
4. **Resolver:** presiona "Resolver". Los dos algoritmos corren en paralelo y se muestran las métricas comparativas.

## Endpoints de la API

| Método | Ruta             | Descripción                            |
|--------|------------------|----------------------------------------|
| GET    | /                | Sirve el frontend                      |
| GET    | /api/health      | Verifica que el servidor esté corriendo|
| POST   | /api/generate    | Genera un laberinto aleatorio          |
| POST   | /api/solve       | Resuelve con BFS o DFS                 |
| POST   | /api/compare     | Resuelve con ambos algoritmos          |

## Valores del grid

| Valor | Significado |
|-------|-------------|
| 0     | Celda libre |
| 1     | Pared       |
| 2     | Inicio      |
| 3     | Meta        |

## Complejidad computacional

| Algoritmo | Temporal | Espacial | Camino óptimo |
|-----------|----------|----------|---------------|
| BFS       | O(V+E)   | O(V)     | Sí            |
| DFS       | O(V+E)   | O(V)     | No            |

En un grid de F×C celdas: V = F·C, E ≤ 4V, por lo tanto ambos son O(F·C) en tiempo y espacio.

## Tests

```bash
python -m tests.test_comparison   # comparación BFS vs DFS
python -m tests.test_metrics      # experimento de escalabilidad
python -m tests.test_generator    # pruebas del generador
python -m tests.test_api          # pruebas de la API
```
