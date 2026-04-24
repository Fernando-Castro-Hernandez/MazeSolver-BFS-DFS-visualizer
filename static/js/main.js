/**
 * main.js
 * Orquestador principal: conecta controles, canvases, editor, animator y API.
 */

import * as api from './api.js';
import { MazeCanvas, WALL, FREE, START, END } from './maze-canvas.js';
import { MazeEditor } from './editor.js';
import { MazeAnimator } from './animator.js';


// ============================================================
// ELEMENTOS DEL DOM
// ============================================================
const elements = {
  canvasBfs: document.getElementById('canvas-bfs'),
  canvasDfs: document.getElementById('canvas-dfs'),
  btnGenerate: document.getElementById('btn-generate'),
  btnSolve: document.getElementById('btn-solve'),
  btnClear: document.getElementById('btn-clear'),
  mazeType: document.getElementById('maze-type'),
  mazeSize: document.getElementById('maze-size'),
  speedSlider: document.getElementById('speed'),
  speedWrap: document.getElementById('speed-wrap'),
  toolBtns: document.querySelectorAll('.tool-btn'),
  modeInputs: document.querySelectorAll('input[name="mode"]'),
  toast: document.getElementById('toast'),
};


// ============================================================
// INSTANCIAS GLOBALES
// ============================================================
const bfsCanvas = new MazeCanvas(elements.canvasBfs, { algorithm: 'bfs' });
const dfsCanvas = new MazeCanvas(elements.canvasDfs, { algorithm: 'dfs' });

// El editor sincroniza AMBOS canvas: cualquier cambio se replica.
const editor = new MazeEditor([bfsCanvas, dfsCanvas], () => {
  // Al editar el grid, invalidamos métricas anteriores
  clearMetrics();
});

const animator = new MazeAnimator();


// ============================================================
// ESTADO
// ============================================================
let currentMode = 'instant';  // "instant" o "animated"


// ============================================================
// INICIALIZACIÓN
// ============================================================
async function init() {
  // Verificar que el backend está corriendo
  try {
    await api.health();
  } catch (err) {
    showToast('Servidor no disponible. Inicia Flask con `python app.py`.', 'error');
    return;
  }

  // Generar un laberinto inicial
  await generateMaze();

  // Conectar listeners
  setupEventListeners();
}


function setupEventListeners() {
  elements.btnGenerate.addEventListener('click', generateMaze);
  elements.btnSolve.addEventListener('click', solveMaze);
  elements.btnClear.addEventListener('click', clearSolution);

  // Herramientas
  elements.toolBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      elements.toolBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      editor.setTool(btn.dataset.tool);
    });
  });

  // Modo instantáneo vs animado
  elements.modeInputs.forEach((input) => {
    input.addEventListener('change', (e) => {
      currentMode = e.target.value;
      elements.speedWrap.classList.toggle('active', currentMode === 'animated');
    });
  });

  // Habilitar el slider si ya arranca en modo animado (no es el caso por defecto,
  // pero por si cambia el HTML)
  if (currentMode === 'animated') {
    elements.speedWrap.classList.add('active');
  }
}


// ============================================================
// ACCIONES PRINCIPALES
// ============================================================

async function generateMaze() {
  animator.stopAll();
  clearMetrics();

  const size = parseInt(elements.mazeSize.value);
  const type = elements.mazeType.value;

  // Para "perfect" y "loopy" el tamaño debe ser impar
  const dim = (type === 'open') ? size : (size % 2 === 0 ? size + 1 : size);

  try {
    disableButtons(true);
    const data = await api.generateMaze({
      rows: dim,
      cols: dim,
      type,
      // Sin seed → cada generación es distinta
    });

    bfsCanvas.setGrid(data.grid);
    dfsCanvas.setGrid(data.grid);
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    disableButtons(false);
  }
}


async function solveMaze() {
  animator.stopAll();
  clearMetrics();

  // Validar que el grid tiene inicio y meta
  const grid = bfsCanvas.getGrid();
  if (!gridHasStartAndEnd(grid)) {
    showToast('El laberinto debe tener un inicio (verde) y una meta (roja).', 'error');
    return;
  }

  try {
    disableButtons(true);

    // Limpiar overlays antes de empezar
    bfsCanvas.clearOverlays();
    dfsCanvas.clearOverlays();
    bfsCanvas.draw();
    dfsCanvas.draw();

    // Pedir ambos resultados al backend en una sola llamada
    const { bfs, dfs } = await api.compare(grid);

    if (currentMode === 'instant') {
      // Mostrar resultado final directamente
      bfsCanvas.showResult(bfs);
      dfsCanvas.showResult(dfs);
      renderMetrics(bfs, dfs);
    } else {
      // Modo animado: reproducir ambos en paralelo
      const speed = parseInt(elements.speedSlider.value);
      await Promise.all([
        animator.animate(bfsCanvas, bfs, speed),
        animator.animate(dfsCanvas, dfs, speed),
      ]);
      renderMetrics(bfs, dfs);
    }
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    disableButtons(false);
  }
}


function clearSolution() {
  animator.stopAll();
  bfsCanvas.clearOverlays();
  dfsCanvas.clearOverlays();
  bfsCanvas.draw();
  dfsCanvas.draw();
  clearMetrics();
}


// ============================================================
// MÉTRICAS
// ============================================================

function renderMetrics(bfs, dfs) {
  setMetric('bfs-found', bfs.found ? '✓ Sí' : '✗ No');
  setMetric('dfs-found', dfs.found ? '✓ Sí' : '✗ No');
  setMetricNote('found',
    (bfs.found && dfs.found) ? 'Ambos algoritmos llegaron a la meta.' :
    (!bfs.found && !dfs.found) ? 'No hay camino posible.' :
    'Solo uno de los algoritmos encontró solución.'
  );

  setMetric('bfs-path', `${bfs.path_length} pasos`);
  setMetric('dfs-path', `${dfs.path_length} pasos`);
  setBest('bfs-path', 'dfs-path', bfs.path_length, dfs.path_length, 'min');
  setMetricNote('path',
    bfs.path_length === dfs.path_length ?
      'Ambos encontraron caminos de igual longitud.' :
      `BFS es ${Math.abs(dfs.path_length - bfs.path_length)} paso(s) más corto.`
  );

  setMetric('bfs-visited', bfs.nodes_visited);
  setMetric('dfs-visited', dfs.nodes_visited);
  setBest('bfs-visited', 'dfs-visited', bfs.nodes_visited, dfs.nodes_visited, 'min');
  setMetricNote('visited',
    `Diferencia: ${Math.abs(bfs.nodes_visited - dfs.nodes_visited)} nodos.`
  );

  setMetric('bfs-frontier', bfs.max_frontier_size);
  setMetric('dfs-frontier', dfs.max_frontier_size);
  setBest('bfs-frontier', 'dfs-frontier', bfs.max_frontier_size, dfs.max_frontier_size, 'min');
  setMetricNote('frontier',
    'Tamaño máximo alcanzado por cola (BFS) o pila (DFS).'
  );

  setMetric('bfs-time', `${bfs.execution_time_ms.toFixed(3)} ms`);
  setMetric('dfs-time', `${dfs.execution_time_ms.toFixed(3)} ms`);
  setBest('bfs-time', 'dfs-time', bfs.execution_time_ms, dfs.execution_time_ms, 'min');
  setMetricNote('time',
    'Medido con time.perf_counter() del backend.'
  );

  setMetric('bfs-mem', `${bfs.peak_memory_kb.toFixed(2)} KB`);
  setMetric('dfs-mem', `${dfs.peak_memory_kb.toFixed(2)} KB`);
  setBest('bfs-mem', 'dfs-mem', bfs.peak_memory_kb, dfs.peak_memory_kb, 'min');
  setMetricNote('mem',
    'Memoria pico medida con tracemalloc.'
  );
}

function setMetric(id, value) {
  const el = document.getElementById(`m-${id}`);
  if (el) el.textContent = value;
}

function setMetricNote(id, note) {
  const el = document.getElementById(`m-${id}-note`);
  if (el) el.textContent = note;
}

function setBest(idA, idB, valA, valB, mode) {
  const elA = document.getElementById(`m-${idA}`);
  const elB = document.getElementById(`m-${idB}`);
  if (!elA || !elB) return;

  elA.classList.remove('best');
  elB.classList.remove('best');

  if (valA === valB) return;

  if (mode === 'min') {
    (valA < valB ? elA : elB).classList.add('best');
  } else {
    (valA > valB ? elA : elB).classList.add('best');
  }
}

function clearMetrics() {
  const ids = ['bfs-found','dfs-found','bfs-path','dfs-path','bfs-visited',
               'dfs-visited','bfs-frontier','dfs-frontier','bfs-time',
               'dfs-time','bfs-mem','dfs-mem'];
  for (const id of ids) {
    const el = document.getElementById(`m-${id}`);
    if (el) {
      el.textContent = '—';
      el.classList.remove('best');
    }
  }
  const noteIds = ['found','path','visited','frontier','time','mem'];
  for (const id of noteIds) {
    const el = document.getElementById(`m-${id}-note`);
    if (el) el.textContent = '—';
  }
}


// ============================================================
// UTILIDADES
// ============================================================

function gridHasStartAndEnd(grid) {
  let hasStart = false, hasEnd = false;
  for (const row of grid) {
    for (const cell of row) {
      if (cell === START) hasStart = true;
      if (cell === END) hasEnd = true;
    }
  }
  return hasStart && hasEnd;
}

function disableButtons(disabled) {
  elements.btnGenerate.disabled = disabled;
  elements.btnSolve.disabled = disabled;
  elements.btnClear.disabled = disabled;
}

function showToast(message, type = '') {
  const toast = elements.toast;
  toast.textContent = message;
  toast.className = 'toast show';
  if (type) toast.classList.add(type);

  setTimeout(() => {
    toast.classList.remove('show');
  }, 3500);
}


// ============================================================
// ARRANQUE
// ============================================================
init();
