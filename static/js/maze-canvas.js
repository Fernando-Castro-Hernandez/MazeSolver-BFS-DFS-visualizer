/**
 * maze-canvas.js
 * Clase MazeCanvas: encapsula el dibujado de un laberinto en un <canvas>.
 *
 * Responsabilidades:
 *   - Mantener el estado del grid (matriz 2D).
 *   - Dibujar el grid, el camino, las celdas exploradas, inicio/meta.
 *   - Convertir coordenadas de píxel a celda (para clicks del usuario).
 *   - Redimensionarse automáticamente al tamaño disponible.
 *
 * Valores del grid (coinciden con el backend):
 *   0 = libre, 1 = pared, 2 = inicio, 3 = meta
 */

// Constantes del grid
export const FREE = 0;
export const WALL = 1;
export const START = 2;
export const END = 3;

// Paleta de colores (debe coincidir con el CSS)
const COLORS = {
  free:     '#fdfbf4',
  wall:     '#0f172a',
  start:    '#059669',
  end:      '#dc2626',
  explored: '#fbbf24',
  pathBfs:  '#b45309',
  pathDfs:  '#1e40af',
  frontier: '#f59e0b',
  grid:     '#ece6d5',
};


export class MazeCanvas {
  /**
   * @param {HTMLCanvasElement} canvas
   * @param {object} options
   * @param {string} options.algorithm - "bfs" o "dfs", determina color del camino
   */
  constructor(canvas, { algorithm = 'bfs' } = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.algorithm = algorithm;

    // Estado del laberinto
    this.grid = null;    // matriz 2D de números
    this.rows = 0;
    this.cols = 0;
    this.cellSize = 0;   // tamaño de cada celda en píxeles (se calcula al redimensionar)

    // Overlays dinámicos (se dibujan encima del grid base)
    this.exploredSet = new Set();  // celdas exploradas: "r,c"
    this.pathSet = new Set();      // celdas del camino final
    this.frontierCell = null;      // celda "actual" durante animación

    // Redimensionado automático
    this._setupResize();
  }

  /**
   * Carga un grid nuevo y lo dibuja.
   */
  setGrid(grid) {
    this.grid = grid.map(row => [...row]);  // copia defensiva
    this.rows = grid.length;
    this.cols = grid[0].length;
    this.clearOverlays();
    this._resize();
    this.draw();
  }

  /**
   * Devuelve una copia del grid actual (para enviar al backend).
   */
  getGrid() {
    return this.grid.map(row => [...row]);
  }

  /**
   * Modifica una celda y redibuja solo esa celda (eficiente).
   * Mantiene la unicidad de inicio y meta automáticamente.
   */
  setCell(r, c, value) {
    if (!this.grid || r < 0 || r >= this.rows || c < 0 || c >= this.cols) return;

    // Si se está colocando un inicio o meta, quitar el anterior
    if (value === START) this._removeFirst(START);
    if (value === END) this._removeFirst(END);

    this.grid[r][c] = value;
    this._drawCell(r, c);
  }

  /**
   * Devuelve la celda correspondiente a un evento de mouse,
   * o null si está fuera del grid.
   */
  cellFromEvent(event) {
    const rect = this.canvas.getBoundingClientRect();
    const scaleX = this.canvas.width / rect.width;
    const scaleY = this.canvas.height / rect.height;
    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;

    const c = Math.floor(x / this.cellSize);
    const r = Math.floor(y / this.cellSize);

    if (r < 0 || r >= this.rows || c < 0 || c >= this.cols) return null;
    return { r, c };
  }

  /**
   * Limpia los overlays (camino, explorado, frontera) sin tocar el grid.
   */
  clearOverlays() {
    this.exploredSet.clear();
    this.pathSet.clear();
    this.frontierCell = null;
  }

  /**
   * Dibuja todo desde cero.
   */
  draw() {
    if (!this.grid) return;
    const { ctx, cellSize, rows, cols } = this;

    // Fondo
    ctx.fillStyle = COLORS.free;
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Celdas
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        this._drawCell(r, c, false);  // sin borde
      }
    }

    // Grid lines muy sutiles (solo si las celdas son grandes)
    if (cellSize >= 16) {
      ctx.strokeStyle = COLORS.grid;
      ctx.lineWidth = 1;
      for (let i = 0; i <= rows; i++) {
        ctx.beginPath();
        ctx.moveTo(0, i * cellSize);
        ctx.lineTo(cols * cellSize, i * cellSize);
        ctx.stroke();
      }
      for (let j = 0; j <= cols; j++) {
        ctx.beginPath();
        ctx.moveTo(j * cellSize, 0);
        ctx.lineTo(j * cellSize, rows * cellSize);
        ctx.stroke();
      }
    }
  }

  // ------- Métodos de visualización (para el animador) -------

  markExplored(r, c) {
    this.exploredSet.add(`${r},${c}`);
    this._drawCell(r, c);
  }

  markPath(path) {
    this.pathSet = new Set(path.map(([r, c]) => `${r},${c}`));
    for (const [r, c] of path) {
      this._drawCell(r, c);
    }
  }

  setFrontier(cell) {
    // Borrar la frontera anterior
    if (this.frontierCell) {
      const [pr, pc] = this.frontierCell;
      this.frontierCell = null;
      this._drawCell(pr, pc);
    }
    if (cell) {
      this.frontierCell = cell;
      this._drawCell(cell[0], cell[1]);
    }
  }

  /**
   * Aplica resultados completos de golpe (modo instantáneo).
   */
  showResult(result) {
    this.clearOverlays();

    // Exploración
    for (const [r, c] of result.exploration_order) {
      this.exploredSet.add(`${r},${c}`);
    }

    // Camino
    this.pathSet = new Set(result.path.map(([r, c]) => `${r},${c}`));

    // Redibujar todo
    this.draw();
  }

  // ------- Métodos internos -------

  _drawCell(r, c, withBorder = true) {
    const { ctx, cellSize } = this;
    const x = c * cellSize;
    const y = r * cellSize;
    const v = this.grid[r][c];
    const key = `${r},${c}`;

    // Decidir color según estado (prioridad: inicio/meta > camino > frontera > explorado > tipo base)
    let color;
    if (v === START)      color = COLORS.start;
    else if (v === END)   color = COLORS.end;
    else if (v === WALL)  color = COLORS.wall;
    else if (this.pathSet.has(key)) {
      color = this.algorithm === 'bfs' ? COLORS.pathBfs : COLORS.pathDfs;
    }
    else if (this.frontierCell && this.frontierCell[0] === r && this.frontierCell[1] === c) {
      color = COLORS.frontier;
    }
    else if (this.exploredSet.has(key)) color = COLORS.explored;
    else                                 color = COLORS.free;

    ctx.fillStyle = color;
    ctx.fillRect(x, y, cellSize, cellSize);

    // Borde sutil para las celdas individuales
    if (withBorder && cellSize >= 10) {
      ctx.strokeStyle = COLORS.grid;
      ctx.lineWidth = 1;
      ctx.strokeRect(x + 0.5, y + 0.5, cellSize - 1, cellSize - 1);
    }

    // Marcadores especiales para inicio y meta (letra S/E)
    if ((v === START || v === END) && cellSize >= 14) {
      ctx.fillStyle = '#fff';
      ctx.font = `600 ${Math.floor(cellSize * 0.55)}px "JetBrains Mono", monospace`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(v === START ? 'S' : 'E', x + cellSize / 2, y + cellSize / 2 + 1);
    }
  }

  /**
   * Busca la primera ocurrencia de un valor y la convierte en FREE.
   * Usado para mantener un solo inicio y una sola meta.
   */
  _removeFirst(value) {
    for (let r = 0; r < this.rows; r++) {
      for (let c = 0; c < this.cols; c++) {
        if (this.grid[r][c] === value) {
          this.grid[r][c] = FREE;
          this._drawCell(r, c);
          return;
        }
      }
    }
  }

  _setupResize() {
    // Usa ResizeObserver para redimensionar el canvas cuando su contenedor cambia
    const resizeObserver = new ResizeObserver(() => {
      if (this.grid) {
        this._resize();
        this.draw();
      }
    });
    resizeObserver.observe(this.canvas.parentElement);
  }

  /**
   * Ajusta el tamaño del canvas al tamaño disponible, manteniendo celdas cuadradas.
   * Internamente aumenta la resolución para pantallas retina (devicePixelRatio).
   */
  _resize() {
    if (!this.grid) return;

    const parent = this.canvas.parentElement;
    const availableWidth = parent.clientWidth - 2;  // -2 por el borde
    const dpr = window.devicePixelRatio || 1;

    // Calcular tamaño de celda para que quepa en ancho disponible
    this.cellSize = Math.floor(availableWidth / this.cols);
    if (this.cellSize < 4) this.cellSize = 4;

    const logicalWidth = this.cellSize * this.cols;
    const logicalHeight = this.cellSize * this.rows;

    // Tamaño CSS (visible)
    this.canvas.style.width = `${logicalWidth}px`;
    this.canvas.style.height = `${logicalHeight}px`;

    // Tamaño interno (con DPR para nitidez en retina)
    this.canvas.width = logicalWidth * dpr;
    this.canvas.height = logicalHeight * dpr;

    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // El cellSize que usamos para dibujar es el lógico; el contexto ya escala
  }
}
