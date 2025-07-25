import argparse

import pandas as pd
from colorama import init
from core.config import WebConfig
from core.logger import FileRotatingLogger
from core.utils import execution_time, progress_bar
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from user.models import HardSkillName, Location, Position, SoftSkillName

init(autoreset=True)

data_2_db_logger = FileRotatingLogger(
    WebConfig.LOG_DIR, 'data_2_db.log', debug=settings.DEBUG
).get_logger()


class Command(BaseCommand):
    help = 'Импорт данных из Excel в Location, HardSkillName, SoftSkillName'

    def add_arguments(
        self: 'Command', parser: argparse.ArgumentParser
    ) -> None:
        parser.add_argument(
            '--locations', type=bool, help='Импорт данных с локациями')
        parser.add_argument(
            '--hard_skills', type=bool, help='Импорт данных с hard skills')
        parser.add_argument(
            '--soft_skills', type=bool, help='Импорт данных с soft skills')
        parser.add_argument(
            '--positions', type=bool, help='Импорт данных с должностями')

    def handle(self: 'Command', *args: tuple, **options: dict) -> None:
        tasks = [
            (
                options['locations'],
                Location, 'Locations',
                ('country', 'city')
            ),
            (
                options['hard_skills'],
                HardSkillName, 'HardSkills',
                ('name', 'description')
            ),
            (
                options['soft_skills'],
                SoftSkillName, 'SoftSkills',
                ('name', 'description')
            ),
            (
                options['positions'],
                Position, 'Positions',
                ('category', 'position')
            ),
        ]
        run_all = not any(opt for opt, *_ in tasks)

        for opt, model, sheet, fields in tasks:
            if opt or run_all:
                self.import_generic(model, sheet, fields)

    @execution_time
    def import_generic(
        self: 'Command',
        model: Location | SoftSkillName | HardSkillName | Position,
        sheet_name: str,
        fields: tuple[str, ...]
    ) -> None:
        df = self._read_cleaned_df(sheet_name)
        total = len(df)

        for index, row in df.iterrows():
            progress_bar(index, total, f'Импорт данных в {model.__name__}: ')

            cleaned_values = []
            for field in fields:
                val = self.valid_str_value(row.get(field))
                val = self.valid_name_value(val) if field in {
                    'country', 'city', 'category', 'position', 'description',
                } else val
                cleaned_values.append(val)

            if all(cleaned_values):
                try:
                    model.update_or_create_normalized(*cleaned_values)
                except ValidationError as e:
                    data_2_db_logger.warning(
                        f'{cleaned_values} -- ошибка: {e}')

    @staticmethod
    def valid_str_value(value: str | None) -> str | None:
        return stripped if (
            value and (stripped := str(value).strip())
        ) else None

    @staticmethod
    def valid_name_value(value: str | None) -> str | None:
        return value[0].upper() + value[1:] if value else value

    def _read_cleaned_df(self: 'Command', sheet_name: str) -> pd.DataFrame:
        df = pd.read_excel(WebConfig.DATA_2_DB_PATH, sheet_name)
        return (
            df.where(pd.notna(df), None).drop_duplicates()
            .reset_index(drop=True)
        )
