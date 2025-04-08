import os
from typing import Final, Optional

from dotenv import load_dotenv

from .exceptions import ConfigEnvError, ConfigDirError, ConfigFileError


ROOT_DIR: Final[str] = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..'))

ENV_PATH: Final[str] = os.path.join(ROOT_DIR, '.env')
load_dotenv(ENV_PATH)


class Config:
    def validate_env_vars(self, env_vars: dict[str, Optional[str]]) -> None:
        missing_vars = [
            var_name
            for var_name, var_value in env_vars.items()
            if var_value is None
        ]

        if missing_vars:
            raise ConfigEnvError(missing_vars)

    def check_dir_path(self, check_dir_path: list[str]) -> None:
        not_exist_dir = [
            dir_path
            for dir_path in check_dir_path
            if not os.path.isdir(dir_path)
        ]
        if not_exist_dir:
            raise ConfigDirError(not_exist_dir)

    def check_file_path(self, check_file_path: list[str]) -> None:
        not_exist_file = [
            file_path
            for file_path in check_file_path
            if not os.path.isfile(file_path)
        ]
        if not_exist_file:
            raise ConfigFileError(not_exist_file)


class WebConfig(Config):
    def __init__(self) -> None:
        self.SECRET_KEY: Optional[str] = os.getenv('WEB_SECRET_KEY')
        self.EMAIL_SERVER: Optional[str] = os.getenv('WEB_EMAIL_SERVER')
        self.EMAIL_PORT: int = int(os.getenv('WEB_EMAIL_PORT', 587))
        self.EMAIL_LOGIN: Optional[str] = os.getenv('WEB_EMAIL_LOGIN')
        self.EMAIL_PSWD: Optional[str] = os.getenv('WEB_EMAIL_PSWD')
        self.EMAIL_PSWD_RESET_TIMEOUT: int = int(os.getenv(
            'WEB_EMAIL_PSWD_RESET_TIMEOUT', 14400))

        self.MEDIA_DIR: str = os.path.join(ROOT_DIR, 'media')
        self.TEMPLATES_DIR: str = os.path.join(ROOT_DIR, 'templates')

        self.validate_env_vars({
            'WEB_SECRET_KEY': self.SECRET_KEY,
            'WEB_EMAIL_SERVER': self.EMAIL_SERVER,
            'WEB_EMAIL_LOGIN': self.EMAIL_LOGIN,
            'WEB_EMAIL_PSWD': self.EMAIL_PSWD,
        })

        self.check_dir_path([self.MEDIA_DIR, self.TEMPLATES_DIR])
        self.check_file_path([ENV_PATH])


web_config = WebConfig()
