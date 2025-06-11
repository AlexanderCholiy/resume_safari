import os
from datetime import timedelta
from typing import Final, Optional
from urllib.parse import urljoin

from dotenv import load_dotenv

from .exceptions import ConfigDirError, ConfigEnvError, ConfigFileError

ROOT_DIR: Final[str] = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..'))

ENV_PATH: Final[str] = os.path.join(ROOT_DIR, '.env')
load_dotenv(ENV_PATH)


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
    SECRET_KEY: str = os.getenv('WEB_SECRET_KEY', 'AvSvUHtySMJqvv0foarXSl243b')
    ACCESS_TOKEN_LIFETIME = timedelta(
        seconds=int(os.getenv('ACCESS_TOKEN_SEC_LIFETIME', 86400))
    )
    EMAIL_SERVER: str = os.getenv(
        'WEB_EMAIL_SERVER' or 'smtp.yandex.ru')
    EMAIL_PORT: int = int(os.getenv('WEB_EMAIL_PORT', 587))
    EMAIL_LOGIN: str = os.getenv('WEB_EMAIL_LOGIN', 'test@mail.com')
    EMAIL_PSWD: str = os.getenv('WEB_EMAIL_PSWD', 'PFbkYwXFABJv')
    EMAIL_PSWD_RESET_TIMEOUT: int = int(
        os.getenv('WEB_EMAIL_PSWD_RESET_TIMEOUT', 900))
    EMAIL_LOGIN_RESET_TIMEOUT: int = int(
        os.getenv('WEB_EMAIL_LOGIN_RESET_TIMEOUT', 1800))

    MEDIA_DIR: str = os.path.join(ROOT_DIR, 'media')
    TEMPLATES_DIR: str = os.path.join(ROOT_DIR, 'templates')
    STATIC_DIR: str = os.path.join(ROOT_DIR, 'static')
    STATIC_ROOT: str = os.path.join(ROOT_DIR, 'collected_static')
    DATA_DIR: str = os.path.join(ROOT_DIR, 'data')
    DATA_2_DB_PATH: str = os.path.join(DATA_DIR, 'data_2_db.xlsx')
    EMAIL_DIR: str = os.path.join(DATA_DIR, 'email_outbox')

    DOMAIN_NAME: str = os.getenv('DOMAIN_NAME', 'http://localhost:8000')
    PREFIX: str = os.getenv('PREFIX', '')
    FULL_SITE_URL: str = urljoin(DOMAIN_NAME, PREFIX)
    MAX_EMAIL_AGE = timedelta(days=1)
    MIN_WAIT_EMAIL = timedelta(seconds=30)
    HOST = os.getenv('HOST', '127.0.0.1')

    LOG_DIR = os.path.join(ROOT_DIR, 'log')
    DEBUG: bool = True if (
        os.getenv('DEBUG', 'False').lower()
    ) in ('true', '1', 'yes', 'y') else False

    DB_NAME: str = os.getenv('POSTGRES_DB', 'django_db')
    DB_USER: str = os.getenv('POSTGRES_USER', 'django_user')
    DB_PASSWORD: str = os.getenv('POSTGRES_PASSWORD', 'django_password')
    DB_HOST: str = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT: str = os.getenv('DB_PORT', 5432)
