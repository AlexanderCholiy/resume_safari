import re
import shutil
from datetime import datetime
from typing import Callable, List, TypeVar

from colorama import Fore, Style
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
    grid = [[[] for _ in range(max_cols)] for _ in range(max_rows)]
    for model in models.order_by('grid_row', 'grid_column', 'updated_at'):
        row = model.grid_row - 1
        col = model.grid_column - 1
        if 0 <= row < max_rows and 0 <= col < max_cols:
            grid[row][col].append(model)

    last_row = -1
    for i in range(max_rows - 1, -1, -1):
        if any(grid[i][j] for j in range(max_cols)):
            last_row = i
            break

    last_col = -1
    for j in range(max_cols - 1, -1, -1):
        if any(grid[i][j] for i in range(max_rows)):
            last_col = j
            break

    if last_row == -1 or last_col == -1:
        return []

    trimmed_grid = [row[:last_col + 1] for row in grid[:last_row + 1]]
    return trimmed_grid


def grid_contains_any_items(grid: list[list[list]]) -> bool:
    for row in grid:
        for cell in row:
            if cell:
                return True
    return False


def progress_bar(
    iteration: int,
    total: int,
    message: str = 'Загрузка: ',
    bar_color: str = Fore.LIGHTGREEN_EX,
) -> None:
    if total == 0:
        return

    terminal_width = shutil.get_terminal_size((80, 20)).columns
    iteration += 1

    percent = round((iteration / total) * 100, 2)
    count_info = f'[{percent}% ({iteration}/{total})]'
    bar_length = 30
    right_padding: int = 3

    filled_length = int(bar_length * iteration // total)
    bar = (
        f'{bar_color}█' * filled_length
        + f'{Fore.LIGHTBLACK_EX}█' * (bar_length - filled_length)
    )
    bar_display = f'{Fore.BLACK}|{bar}{Fore.BLACK}|'

    left_part = f'{Fore.BLUE}{message}{Fore.WHITE}{count_info}'
    left_length = len(strip_ansi(left_part))
    bar_length_real = len(strip_ansi(bar_display))
    padding = terminal_width - left_length - bar_length_real - right_padding
    if padding < 1:
        padding = 1
    spacer = ' ' * padding
    end_space = ' ' * right_padding

    print(f'{left_part}{spacer}{bar_display}{end_space}', end='\r')

    if iteration == total:
        print(Style.RESET_ALL)


def strip_ansi(text: str) -> str:
    """Удаляет ANSI-коды из строки для корректного измерения длины."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)


def execution_time(func: Callable[..., T]) -> Callable[..., T]:
    def wrapper(*args: tuple, **kwargs: dict) -> T:
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            execution_time = datetime.now() - start_time
            total_seconds = execution_time.total_seconds()
            message_part_1 = (
                f'{Fore.BLUE}Функция '
                f'{Style.RESET_ALL}'
                f'{func.__name__} '
                f'{Fore.BLUE}выполнялась '
                f'{Style.RESET_ALL}'
            )

            if total_seconds >= 60:
                minutes = int(total_seconds // 60)
                seconds = int(total_seconds % 60)
                message = f'{message_part_1}{minutes} мин. {seconds} сек.'
            elif total_seconds >= 1:
                seconds = round(total_seconds, 2)
                message = f'{message_part_1}{seconds} сек.'
            else:
                milliseconds = round(execution_time.microseconds / 1000, 2)
                message = f'{message_part_1}{milliseconds} мс.'

            print(message + Style.RESET_ALL)

    return wrapper
