from typing import List, TypeVar
from django.db.models import QuerySet

from .constants import MAX_GRID_SIZE_X, MAX_GRID_SIZE_Y


T = TypeVar('T')


def build_grid(
    models: QuerySet,
    max_rows: int = MAX_GRID_SIZE_Y,
    max_cols: int = MAX_GRID_SIZE_X,
) -> List[List[List[T]]]:
    """
    Формирует сетку (матрицу) для моделей наследованных от Grid,
    отсортированных по координатам и дате.
    После построения удаляет пустые строки и столбцы с конца,
    чтобы не оставалось пустых ячеек после последней непустой.
    """
    # Шаг 1: построить полную сетку
    grid = [[[] for _ in range(max_cols)] for _ in range(max_rows)]
    for model in models.order_by('grid_row', 'grid_column', 'updated_at'):
        row = model.grid_row - 1
        col = model.grid_column - 1
        if 0 <= row < max_rows and 0 <= col < max_cols:
            grid[row][col].append(model)

    # Шаг 2: найти индекс последней непустой строки
    last_row = -1
    for i in range(max_rows - 1, -1, -1):
        if any(grid[i][j] for j in range(max_cols)):
            last_row = i
            break

    # Шаг 3: найти индекс последнего непустого столбца
    last_col = -1
    for j in range(max_cols - 1, -1, -1):
        if any(grid[i][j] for i in range(max_rows)):
            last_col = j
            break

    # Шаг 4: обрезать сетку
    if last_row == -1 or last_col == -1:
        return []  # полностью пустая сетка

    trimmed_grid = [row[:last_col + 1] for row in grid[:last_row + 1]]
    return trimmed_grid


def grid_contains_any_items(grid: list[list[list]]) -> bool:
    for row in grid:
        for cell in row:
            if cell:
                return True
    return False
