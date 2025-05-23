import os
from typing import Final, Optional

from dotenv import load_dotenv

from .exceptions import ConfigEnvError, ConfigDirError, ConfigFileError


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
    SECRET_KEY: Optional[str] = os.getenv('WEB_SECRET_KEY')
    EMAIL_SERVER: Optional[str] = os.getenv('WEB_EMAIL_SERVER')
    EMAIL_PORT: int = int(os.getenv('WEB_EMAIL_PORT', 587))
    EMAIL_LOGIN: Optional[str] = os.getenv('WEB_EMAIL_LOGIN')
    EMAIL_PSWD: Optional[str] = os.getenv('WEB_EMAIL_PSWD')
    EMAIL_PSWD_RESET_TIMEOUT: int = int(
        os.getenv('WEB_EMAIL_PSWD_RESET_TIMEOUT'))
    EMAIL_LOGIN_RESET_TIMEOUT: int = int(
        os.getenv('WEB_EMAIL_LOGIN_RESET_TIMEOUT'))

    MEDIA_DIR: str = os.path.join(ROOT_DIR, 'media')
    TEMPLATES_DIR: str = os.path.join(ROOT_DIR, 'templates',)
    STATIC_DIR: str = os.path.join(ROOT_DIR, 'static')

    @staticmethod
    def validate() -> None:
        WebConfig().validate_env_vars({
            'WEB_SECRET_KEY': WebConfig.SECRET_KEY,
            'WEB_EMAIL_SERVER': WebConfig.EMAIL_SERVER,
            'WEB_EMAIL_LOGIN': WebConfig.EMAIL_LOGIN,
            'WEB_EMAIL_PSWD': WebConfig.EMAIL_PSWD,
        })
        WebConfig().check_dirs([WebConfig.MEDIA_DIR, WebConfig.TEMPLATES_DIR])
        WebConfig().check_files([ENV_PATH])
