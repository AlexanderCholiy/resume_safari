import os
from datetime import timedelta
from typing import Final, Optional
from dotenv import load_dotenv

from .exceptions import ConfigDirError, ConfigEnvError, ConfigFileError

ROOT_DIR: Final[str] = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..'))

ENV_PATH: Final[str] = os.path.join(ROOT_DIR, '.env')


class Config:
    def _raise_if_missing(
        self: 'Config',
        items: list[str],
        check_func: callable,
        error_cls: ConfigEnvError | ConfigDirError | ConfigFileError
    ) -> None:
        missing = [item for item in items if not check_func(item)]
        if missing:
            raise error_cls(missing)

    def validate_env_vars(
        self: 'Config', env_vars: dict[str, Optional[str]]
    ) -> None:
        missing_vars = [name for name, val in env_vars.items() if val is None]
        if missing_vars:
            raise ConfigEnvError(missing_vars)

    def check_dirs(self: 'Config', dirs: list[str]) -> None:
        self._raise_if_missing(dirs, os.path.isdir, ConfigDirError)

    def check_files(self: 'Config', files: list[str]) -> None:
        self._raise_if_missing(files, os.path.isfile, ConfigFileError)


class WebConfig(Config):
    MAX_EMAIL_AGE = timedelta(days=1)
    MIN_WAIT_EMAIL = timedelta(seconds=30)
    ACCESS_TOKEN_LIFETIME = timedelta(seconds=86400)

    EMAIL_PORT: int = 587
    DB_PORT: int = 5432
    EMAIL_PSWD_RESET_TIMEOUT: int = 900
    EMAIL_LOGIN_RESET_TIMEOUT: int = 1800

    MEDIA_DIR: str = os.path.join(ROOT_DIR, 'media')
    TEMPLATES_DIR: str = os.path.join(ROOT_DIR, 'templates')
    STATIC_DIR: str = os.path.join(ROOT_DIR, 'static')
    STATIC_ROOT: str = os.path.join(ROOT_DIR, 'collected_static')
    DATA_DIR: str = os.path.join(ROOT_DIR, 'data')
    DATA_2_DB_PATH: str = os.path.join(DATA_DIR, 'data_2_db.xlsx')
    EMAIL_DIR: str = os.path.join(DATA_DIR, 'email_outbox')
    LOG_DIR = os.path.join(ROOT_DIR, 'log')

    def __init__(self: 'WebConfig') -> None:
        super().__init__()
        load_dotenv(ENV_PATH, override=True)

        self.DOMAIN_NAME: str = os.getenv(
            'DOMAIN_NAME', 'http://localhost:8000')
        self.HOST = os.getenv('HOST', '127.0.0.1')
        self.SECRET_KEY: str = os.getenv('WEB_SECRET_KEY', 'AvSvUHtySMJqarXSl')

        self.EMAIL_SERVER: str = os.getenv(
            'WEB_EMAIL_SERVER', 'smtp.yandex.ru')
        self.EMAIL_LOGIN: str = os.getenv('WEB_EMAIL_LOGIN', 'test@mail.com')
        self.EMAIL_PSWD: str = os.getenv('WEB_EMAIL_PSWD', 'PFbkYwXFABJv')

        self.DEBUG: bool = True if (
            os.getenv('DEBUG', 'False').lower()
        ) in ('true', '1', 'yes', 'y') else False

        self.DB_NAME: str = os.getenv('POSTGRES_DB', 'django_db')
        self.DB_USER: str = os.getenv('POSTGRES_USER', 'django_user')
        self.DB_PASSWORD: str = os.getenv('POSTGRES_PASSWORD', 'django_pswd')
        self.DB_HOST: str = os.getenv('DB_HOST', '127.0.0.1')


web_config = WebConfig()
