class ConfigEnvError(Exception):
    """Ошибка: отсутствуют необходимые переменные окружения."""

    def __init__(self, missing_vars: list[str]):
        joined_vars = '\n- '.join(missing_vars)
        message = (
            'Ошибка конфигурации: отсутствуют переменные окружения:\n'
            f'- {joined_vars}'
        )
        super().__init__(message)


class ConfigDirError(Exception):
    """Ошибка: указанные директории не существуют."""

    def __init__(self, missing_dirs: list[str]):
        joined_dirs = '\n- '.join(missing_dirs)
        message = (
            'Ошибка конфигурации: не найдены следующие директории:\n'
            f'- {joined_dirs}'
        )
        super().__init__(message)


class ConfigFileError(Exception):
    """Ошибка: указанные файлы не существуют."""

    def __init__(self, missing_files: list[str]):
        joined_files = '\n- '.join(missing_files)
        message = (
            'Ошибка конфигурации: не найдены следующие файлы:\n'
            f'- {joined_files}'
        )
        super().__init__(message)
