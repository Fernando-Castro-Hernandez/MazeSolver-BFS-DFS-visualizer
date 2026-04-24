"""
metrics.py
Módulo para medir métricas físicas (tiempo y memoria) de los algoritmos
de búsqueda.

Filosofía de diseño:
    - Las métricas ESTRUCTURALES (nodos visitados, tamaño de frontera)
      están dentro de los algoritmos porque dependen de su estado interno.
    - Las métricas FÍSICAS (tiempo, memoria heap) se miden desde afuera
      con un wrapper, para mantener los algoritmos puros.

Esto separa responsabilidades:
    bfs() / dfs()  → resuelven el problema.
    measure()      → mide cómo lo resolvieron.
"""

import time
import tracemalloc
from typing import Callable


def measure(algorithm_fn: Callable, *args, **kwargs) -> dict:
    """
    Ejecuta un algoritmo y mide su tiempo y memoria física.

    Args:
        algorithm_fn: función a ejecutar (bfs o dfs).
        *args, **kwargs: argumentos que se pasan a la función.

    Returns:
        dict con todas las métricas del algoritmo + las métricas físicas:
            - execution_time_ms:  tiempo de ejecución en milisegundos
            - execution_time_us:  tiempo en microsegundos (más preciso)
            - peak_memory_bytes:  pico de memoria usado durante la ejecución
            - peak_memory_kb:     lo mismo en KB para legibilidad
    """
    # --- Iniciar medición de memoria ---
    # tracemalloc rastrea todas las asignaciones de memoria de Python.
    # Hay que iniciarlo antes de la función y leer el pico al final.
    tracemalloc.start()

    # --- Medir tiempo ---
    # perf_counter() da nanosegundos de precisión y es monotónico
    # (nunca salta hacia atrás, a diferencia de time.time()).
    start_time = time.perf_counter()

    # Ejecutar el algoritmo
    result = algorithm_fn(*args, **kwargs)

    elapsed_seconds = time.perf_counter() - start_time

    # --- Leer pico de memoria y detener medición ---
    # get_traced_memory() devuelve (actual, pico) en bytes.
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # --- Agregar métricas físicas al resultado ---
    result["execution_time_ms"] = elapsed_seconds * 1_000
    result["execution_time_us"] = elapsed_seconds * 1_000_000
    result["peak_memory_bytes"] = peak_memory
    result["peak_memory_kb"] = peak_memory / 1024

    return result


def measure_average(algorithm_fn: Callable, runs: int = 5, *args, **kwargs) -> dict:
    """
    Ejecuta un algoritmo varias veces y devuelve el resultado con métricas
    promediadas. Útil para reducir ruido en mediciones de tiempo muy cortas.

    Args:
        algorithm_fn: función a ejecutar.
        runs: número de ejecuciones. Por defecto 5.
        *args, **kwargs: argumentos del algoritmo.

    Returns:
        dict con el resultado del último run + tiempo promedio, mín y máx.
    """
    if runs < 1:
        raise ValueError("runs debe ser al menos 1")

    times_ms = []
    memory_bytes = []
    result = None

    for _ in range(runs):
        result = measure(algorithm_fn, *args, **kwargs)
        times_ms.append(result["execution_time_ms"])
        memory_bytes.append(result["peak_memory_bytes"])

    # Agregar estadísticas
    result["avg_time_ms"] = sum(times_ms) / runs
    result["min_time_ms"] = min(times_ms)
    result["max_time_ms"] = max(times_ms)
    result["avg_memory_bytes"] = sum(memory_bytes) / runs
    result["runs"] = runs

    return result


def format_metrics(result: dict) -> str:
    """
    Formatea las métricas de un resultado para impresión legible.
    """
    lines = [
        f"Algoritmo:            {result['algorithm']}",
        f"Camino encontrado:    {result['found']}",
        f"Longitud del camino:  {result['path_length']} pasos",
        f"Nodos visitados:      {result['nodes_visited']}",
        f"Frontera máxima:      {result['max_frontier_size']}",
        f"Tiempo de ejecución:  {result['execution_time_ms']:.4f} ms "
        f"({result['execution_time_us']:.1f} μs)",
        f"Memoria pico:         {result['peak_memory_kb']:.2f} KB "
        f"({result['peak_memory_bytes']} bytes)",
    ]

    # Si es resultado de measure_average, añadir estadísticas
    if "avg_time_ms" in result:
        lines.append(f"Tiempo promedio ({result['runs']} runs): "
                     f"{result['avg_time_ms']:.4f} ms "
                     f"[min: {result['min_time_ms']:.4f}, max: {result['max_time_ms']:.4f}]")

    return "\n".join(lines)
