/**
 * editor.js
 * Permite al usuario editar el laberinto con el cursor.
 *
 * Conceptos clave:
 *   - Dos canvas en la pantalla, pero comparten el mismo grid (cambiar en uno
 *     debe reflejarse en el otro). Por eso el editor sincroniza ambos.
 *   - Click-and-drag para pintar paredes en bloque.
 *   - Herramientas: pared, borrar, inicio, meta.
 */

import { WALL, FREE, START, END } from './maze-canvas.js';


export class MazeEditor {
  /**
   * @param {MazeCanvas[]} canvases - lista de canvas que deben mantenerse sincronizados
   * @param {function} onChange     - callback llamado cuando el grid cambia
   */
  constructor(canvases, onChange = () => {}) {
    this.canvases = canvases;
    this.onChange = onChange;
    this.currentTool = 'wall';
    this.isDragging = false;
    this.lastCell = null;       // evita procesar la misma celda dos veces en un drag

    this._bindEvents();
  }

  setTool(tool) {
    this.currentTool = tool;
  }

  _bindEvents() {
    for (const canvas of this.canvases) {
      const el = canvas.canvas;

      el.addEventListener('mousedown', (e) => this._onDown(e, canvas));
      el.addEventListener('mousemove', (e) => this._onMove(e, canvas));
      el.addEventListener('mouseup',   () => this._onUp());
      el.addEventListener('mouseleave',() => this._onUp());

      // Touch support para móviles/tablets
      el.addEventListener('touchstart', (e) => this._onTouch(e, canvas, 'down'), { passive: false });
      el.addEventListener('touchmove',  (e) => this._onTouch(e, canvas, 'move'), { passive: false });
      el.addEventListener('touchend',   () => this._onUp());

      // Evitar menú contextual al hacer click derecho
      el.addEventListener('contextmenu', (e) => e.preventDefault());
    }
  }

  _onDown(event, canvas) {
    if (event.button !== 0) return;  // solo botón izquierdo
    this.isDragging = true;
    this.lastCell = null;
    this._applyTool(event, canvas);
  }

  _onMove(event, canvas) {
    if (!this.isDragging) return;
    this._applyTool(event, canvas);
  }

  _onUp() {
    this.isDragging = false;
    this.lastCell = null;
  }

  _onTouch(event, canvas, type) {
    event.preventDefault();
    if (event.touches.length === 0 && type === 'move') return;

    const touch = event.touches[0];
    if (!touch) return;

    // Simular MouseEvent para reutilizar la lógica
    const fakeEvent = { clientX: touch.clientX, clientY: touch.clientY, button: 0 };

    if (type === 'down') this._onDown(fakeEvent, canvas);
    else if (type === 'move') this._onMove(fakeEvent, canvas);
  }

  _applyTool(event, canvas) {
    const cell = canvas.cellFromEvent(event);
    if (!cell) return;

    // Evitar procesar la misma celda repetidamente en un drag
    const key = `${cell.r},${cell.c}`;
    if (this.lastCell === key) return;
    this.lastCell = key;

    const grid = canvas.grid;
    const current = grid[cell.r][cell.c];

    // No permitir sobrescribir inicio/meta con pared/borrar
    // (para cambiarlos hay que usar específicamente la herramienta)
    if ((current === START || current === END) &&
        (this.currentTool === 'wall' || this.currentTool === 'free')) {
      return;
    }

    let newValue;
    switch (this.currentTool) {
      case 'wall':  newValue = WALL; break;
      case 'free':  newValue = FREE; break;
      case 'start': newValue = START; break;
      case 'end':   newValue = END; break;
      default: return;
    }

    if (current === newValue) return;  // sin cambios

    // Aplicar el cambio a TODOS los canvas sincronizados
    for (const cv of this.canvases) {
      cv.setCell(cell.r, cell.c, newValue);
    }

    this.onChange();
  }
}
