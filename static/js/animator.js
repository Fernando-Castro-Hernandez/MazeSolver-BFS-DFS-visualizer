/**
 * animator.js
 * Reproduce la exploración de BFS/DFS paso a paso en un canvas.
 *
 * Estrategia: usar requestAnimationFrame y un contador de pasos por frame
 * para permitir diferentes velocidades. En cada frame procesamos N celdas
 * (N depende de la velocidad elegida).
 */


export class MazeAnimator {
  constructor() {
    this.currentAnimations = [];  // referencias a animaciones activas (para cancelar)
  }

  /**
   * Detiene todas las animaciones en curso.
   */
  stopAll() {
    for (const anim of this.currentAnimations) {
      anim.cancelled = true;
      if (anim.rafId) cancelAnimationFrame(anim.rafId);
    }
    this.currentAnimations = [];
  }

  /**
   * Anima la exploración de un resultado en un MazeCanvas.
   *
   * @param {MazeCanvas} canvas        - donde dibujar
   * @param {object} result            - resultado del backend (tiene exploration_order y path)
   * @param {number} speed             - 1 (lento) a 100 (rápido)
   * @returns {Promise<void>}          - se resuelve cuando termina la animación
   */
  animate(canvas, result, speed = 60) {
    return new Promise((resolve) => {
      canvas.clearOverlays();
      canvas.draw();

      const explorationOrder = result.exploration_order;
      const path = result.path;

      if (!explorationOrder || explorationOrder.length === 0) {
        resolve();
        return;
      }

      // Calcular celdas por frame según velocidad.
      // speed=1   → 1 celda cada 3 frames (muy lento)
      // speed=50  → 1 celda por frame
      // speed=100 → 20 celdas por frame (muy rápido)
      const cellsPerFrame = Math.max(0.25, Math.pow(speed / 25, 1.8));
      const framesPerCell = cellsPerFrame < 1 ? Math.round(1 / cellsPerFrame) : 1;
      const batchSize = cellsPerFrame >= 1 ? Math.round(cellsPerFrame) : 1;

      const anim = {
        cancelled: false,
        rafId: null,
        index: 0,
        frameCount: 0,
      };
      this.currentAnimations.push(anim);

      const tick = () => {
        if (anim.cancelled) return;

        anim.frameCount++;

        // Solo procesar celdas en ciertos frames si vamos lento
        if (anim.frameCount % framesPerCell === 0) {
          // Procesar un lote de celdas
          for (let i = 0; i < batchSize && anim.index < explorationOrder.length; i++) {
            const [r, c] = explorationOrder[anim.index];
            canvas.markExplored(r, c);
            anim.index++;
          }

          // Marcar la frontera actual (última celda visitada)
          if (anim.index < explorationOrder.length) {
            canvas.setFrontier(explorationOrder[anim.index]);
          }
        }

        if (anim.index < explorationOrder.length) {
          anim.rafId = requestAnimationFrame(tick);
        } else {
          // Exploración terminada, limpiar frontera y dibujar camino
          canvas.setFrontier(null);
          if (path && path.length > 0) {
            this._drawPathProgressively(canvas, path, speed, anim, resolve);
          } else {
            resolve();
          }
        }
      };

      anim.rafId = requestAnimationFrame(tick);
    });
  }

  /**
   * Dibuja el camino final progresivamente (trazo por trazo).
   */
  _drawPathProgressively(canvas, path, speed, anim, resolve) {
    // El camino se dibuja más rápido que la exploración para dar énfasis
    const pathSpeed = Math.min(100, speed * 1.5);
    const cellsPerFrame = Math.max(0.5, Math.pow(pathSpeed / 25, 1.8));
    const framesPerCell = cellsPerFrame < 1 ? Math.round(1 / cellsPerFrame) : 1;
    const batchSize = cellsPerFrame >= 1 ? Math.round(cellsPerFrame) : 1;

    let i = 0;
    let frameCount = 0;
    const currentPathSet = new Set();

    const tick = () => {
      if (anim.cancelled) return;
      frameCount++;

      if (frameCount % framesPerCell === 0) {
        for (let j = 0; j < batchSize && i < path.length; j++) {
          currentPathSet.add(`${path[i][0]},${path[i][1]}`);
          i++;
        }
        canvas.pathSet = currentPathSet;
        // Redibujar solo las celdas del camino agregadas hasta ahora
        for (const [r, c] of path.slice(0, i)) {
          canvas._drawCell(r, c);
        }
      }

      if (i < path.length) {
        anim.rafId = requestAnimationFrame(tick);
      } else {
        resolve();
      }
    };

    anim.rafId = requestAnimationFrame(tick);
  }
}
