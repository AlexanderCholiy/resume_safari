class ConfigError(Exception):
    """Базовый класс для ошибок конфигурации."""

    def __init__(self, items: list[str], message: str):
        self.items = items
        items_str = '\n'.join(items)
        super().__init__(f'Ошибка конфигурации. {message}:\n{items_str}')


class ConfigEnvError(ConfigError):
    """Исключение для отсутствующих переменных окружения."""

    def __init__(self, missing_vars: list[str]):
        super().__init__(missing_vars, 'Отсутствуют переменные окружения')


class ConfigDirError(ConfigError):
    """Исключение для не существующего пути к директории."""

    def __init__(self, not_exist_dir: list[str]):
        super().__init__(not_exist_dir, 'Проверьте существование директорий')


class ConfigFileError(ConfigError):
    """Исключение для не существующего пути к файлу."""

    def __init__(self, not_exist_file: list[str]):
        super().__init__(not_exist_file, 'Проверьте существование файлов')
