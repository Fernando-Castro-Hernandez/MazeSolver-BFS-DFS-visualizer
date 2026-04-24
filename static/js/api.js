/**
 * api.js
 * Wrapper para comunicarse con la API Flask del backend.
 * Todas las funciones son async y lanzan Error con mensaje legible en caso de fallo.
 */

const BASE_URL = '';  // vacío = mismo origen (Flask sirve todo)

/**
 * Wrapper genérico para fetch + JSON + manejo de errores.
 */
async function request(path, options = {}) {
  try {
    const response = await fetch(`${BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });

    const data = await response.json();

    if (!response.ok) {
      // El backend devuelve { error: "mensaje" } con código 4xx/5xx
      throw new Error(data.error || `Error ${response.status}`);
    }

    return data;
  } catch (err) {
    // fetch tira TypeError si no hay conexión al servidor
    if (err instanceof TypeError) {
      throw new Error('No se pudo conectar al servidor. ¿Está corriendo Flask?');
    }
    throw err;
  }
}

/**
 * Verifica que el servidor esté corriendo.
 * @returns {Promise<{status: string, message: string}>}
 */
export async function health() {
  return request('/api/health');
}

/**
 * Genera un laberinto aleatorio.
 * @param {object} opts
 * @param {number} opts.rows     - filas (debe ser impar para perfect/loopy)
 * @param {number} opts.cols     - columnas (debe ser impar para perfect/loopy)
 * @param {string} opts.type     - "perfect" | "open" | "loopy"
 * @param {number} [opts.seed]   - semilla opcional
 * @param {number} [opts.extraOpenings] - solo para "loopy", fracción 0-1
 * @returns {Promise<{grid, rows, cols, start, end}>}
 */
export async function generateMaze({ rows, cols, type = 'perfect', seed, extraOpenings }) {
  const body = { rows, cols, type };
  if (seed !== undefined) body.seed = seed;
  if (extraOpenings !== undefined) body.extra_openings = extraOpenings;

  return request('/api/generate', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * Resuelve un laberinto con un algoritmo específico.
 * @param {number[][]} grid   - matriz del laberinto
 * @param {string} algorithm  - "bfs" o "dfs"
 * @returns {Promise<object>} - resultado con path, métricas, etc.
 */
export async function solve(grid, algorithm) {
  return request('/api/solve', {
    method: 'POST',
    body: JSON.stringify({ grid, algorithm }),
  });
}

/**
 * Resuelve con ambos algoritmos y devuelve ambos resultados.
 * @param {number[][]} grid
 * @returns {Promise<{bfs: object, dfs: object}>}
 */
export async function compare(grid) {
  return request('/api/compare', {
    method: 'POST',
    body: JSON.stringify({ grid }),
  });
}
