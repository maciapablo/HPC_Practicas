a = ["EY","Deloiitte","PwC","KPMG"]

from __future__ import annotations

import os
import random
import time
import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

# ============================================================
# CONFIG
# ============================================================

WIDTH = 39   # Mejor impar
HEIGHT = 21  # Mejor impar
ANIMATION_DELAY = 0.02
SHOW_GENERATION = False
SHOW_SEARCH = True
RANDOM_SEED = None  # Ejemplo: 42 para reproducible

# ============================================================
# UTILS
# ============================================================

def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def clamp_to_odd(n: int, minimum: int = 5) -> int:
    n = max(n, minimum)
    return n if n % 2 == 1 else n + 1


def neighbors_two_steps(x: int, y: int, width: int, height: int) -> List[Tuple[int, int]]:
    dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
    result = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if 1 <= nx < width - 1 and 1 <= ny < height - 1:
            result.append((nx, ny))
    return result


def manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ============================================================
# PRIORITY NODE
# ============================================================

@dataclass(order=True)
class PriorityNode:
    priority: int
    count: int
    position: Tuple[int, int] = field(compare=False)


# ============================================================
# MAZE
# ============================================================

class Maze:
    WALL = "█"
    EMPTY = " "
    START = "S"
    END = "E"
    PATH = "·"
    VISITED = "░"
    FRONTIER = "▒"

    def __init__(self, width: int, height: int, seed: Optional[int] = None) -> None:
        self.width = clamp_to_odd(width)
        self.height = clamp_to_odd(height)
        self.rng = random.Random(seed)

        self.grid: List[List[str]] = [
            [self.WALL for _ in range(self.width)]
            for _ in range(self.height)
        ]

        self.start = (1, 1)
        self.end = (self.width - 2, self.height - 2)

    def generate(self, animate: bool = False, delay: float = 0.01) -> None:
        """Genera un laberinto usando recursive backtracking."""
        stack = [self.start]
        sx, sy = self.start
        self.grid[sy][sx] = self.EMPTY

        while stack:
            x, y = stack[-1]
            unvisited = [
                (nx, ny)
                for nx, ny in neighbors_two_steps(x, y, self.width, self.height)
                if self.grid[ny][nx] == self.WALL
            ]

            if unvisited:
                nx, ny = self.rng.choice(unvisited)

                wall_x = x + (nx - x) // 2
                wall_y = y + (ny - y) // 2

                self.grid[wall_y][wall_x] = self.EMPTY
                self.grid[ny][nx] = self.EMPTY
                stack.append((nx, ny))
            else:
                stack.pop()

            if animate:
                self.render()
                time.sleep(delay)

        self._ensure_start_end_open()

    def _ensure_start_end_open(self) -> None:
        sx, sy = self.start
        ex, ey = self.end

        self.grid[sy][sx] = self.EMPTY
        self.grid[ey][ex] = self.EMPTY

        for x, y in [(sx + 1, sy), (sx, sy + 1), (ex - 1, ey), (ex, ey - 1)]:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x] = self.EMPTY

    def is_walkable(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height and self.grid[y][x] != self.WALL

    def walk_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        result = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                result.append((nx, ny))
        return result

    def reconstruct_path(
        self,
        came_from: Dict[Tuple[int, int], Tuple[int, int]],
        current: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def solve_a_star(
        self,
        animate: bool = False,
        delay: float = 0.02,
    ) -> Tuple[List[Tuple[int, int]], Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        start = self.start
        goal = self.end

        open_heap: List[PriorityNode] = []
        heapq.heappush(open_heap, PriorityNode(0, 0, start))

        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score: Dict[Tuple[int, int], int] = {start: 0}
        f_score: Dict[Tuple[int, int], int] = {start: manhattan(start, goal)}

        open_set: Set[Tuple[int, int]] = {start}
        visited: Set[Tuple[int, int]] = set()

        counter = 0

        while open_heap:
            current = heapq.heappop(open_heap).position

            if current not in open_set:
                continue

            open_set.remove(current)

            if current == goal:
                path = self.reconstruct_path(came_from, current)
                return path, visited, open_set

            visited.add(current)

            for neighbor in self.walk_neighbors(*current):
                tentative_g = g_score[current] + 1

                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + manhattan(neighbor, goal)

                    if neighbor not in open_set and neighbor not in visited:
                        counter += 1
                        heapq.heappush(
                            open_heap,
                            PriorityNode(f_score[neighbor], counter, neighbor)
                        )
                        open_set.add(neighbor)

            if animate:
                self.render(
                    visited=visited,
                    frontier=open_set,
                    path=None,
                    title="Resolviendo laberinto con A*..."
                )
                time.sleep(delay)

        return [], visited, open_set

    def render(
        self,
        visited: Optional[Set[Tuple[int, int]]] = None,
        frontier: Optional[Set[Tuple[int, int]]] = None,
        path: Optional[List[Tuple[int, int]]] = None,
        title: str = "Laberinto",
    ) -> None:
        clear_screen()

        visited = visited or set()
        frontier = frontier or set()
        path_set = set(path or [])

        sx, sy = self.start
        ex, ey = self.end

        output_lines = [title, ""]

        for y in range(self.height):
            row_chars = []
            for x in range(self.width):
                pos = (x, y)

                if pos == (sx, sy):
                    row_chars.append(self.START)
                elif pos == (ex, ey):
                    row_chars.append(self.END)
                elif pos in path_set:
                    row_chars.append(self.PATH)
                elif pos in frontier:
                    row_chars.append(self.FRONTIER)
                elif pos in visited:
                    row_chars.append(self.VISITED)
                else:
                    row_chars.append(self.grid[y][x])

            output_lines.append("".join(row_chars))

        print("\n".join(output_lines))


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    maze = Maze(WIDTH, HEIGHT, seed=RANDOM_SEED)

    maze.generate(animate=SHOW_GENERATION, delay=0.005)
    maze.render(title="Laberinto generado")
    time.sleep(0.7)

    path, visited, frontier = maze.solve_a_star(
        animate=SHOW_SEARCH,
        delay=ANIMATION_DELAY
    )

    if path:
        maze.render(
            visited=visited,
            frontier=frontier,
            path=path,
            title=f"Laberinto resuelto | Longitud del camino: {len(path)} | Nodos explorados: {len(visited)}"
        )
    else:
        maze.render(
            visited=visited,
            frontier=frontier,
            path=None,
            title="No se encontró solución"
        )

    print("\nPulsa Ctrl+C para salir.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma terminado.")