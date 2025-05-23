import argparse
import numpy as np

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from colorama import init

from user.models import Location, HardSkillName, SoftSkillName
from core.utils import progress_bar, execution_time
from core.config import WebConfig


init(autoreset=True)


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

    def handle(self: 'Command', *args: tuple, **options: dict) -> None:
        locations: bool | None = options['locations']
        hard_skills: bool | None = options['hard_skills']
        soft_skills: bool | None = options['soft_skills']
        if not any((locations, hard_skills, soft_skills,)):
            raise ValueError(
                'Укажите один или несколько доступных параметров.'
            )
        if locations:
            self.import_locations()
        if hard_skills:
            self.import_skills(HardSkillName, 'HardSkills')
        if soft_skills:
            self.import_skills(SoftSkillName, 'SoftSkills')

    @execution_time
    def import_locations(self: 'Command') -> None:
        df = pd.read_excel(WebConfig.DATA_2_DB_PATH, 'Locations')
        df = (
            df.where(pd.notna(df), None)
            .drop_duplicates().reset_index(drop=True)
        )
        with transaction.atomic():
            total = len(df)
            for index, row in df.iterrows():
                progress_bar(
                    index, total, f'Импорт данных в {Location.__name__}:')
                country = self.valid_str_value(row['country'])
                country = country.title() if country else country
                city = self.valid_str_value(row['city'])
                city = city.title() if city else city
                if country and city:
                    Location.objects.update_or_create(
                        country=country, city=city)

    @execution_time
    def import_skills(
        self: 'Command', model: HardSkillName | SoftSkillName, sheet_name: str
    ) -> None:
        df = pd.read_excel(WebConfig.DATA_2_DB_PATH, sheet_name)
        df = (
            df.where(pd.notna(df), None)
            .drop_duplicates().reset_index(drop=True)
        )
        with transaction.atomic():
            total = len(df)
            for index, row in df.iterrows():
                progress_bar(
                    index, total, f'Импорт данных в {model.__name__}:')
                name = self.valid_str_value(row['name'])
                description = self.valid_str_value(row['description'])
                if name:
                    model.objects.get_or_create(
                        name=name, description=description)
                    model.objects.update_or_create(
                        name=name,
                        defaults={'description': description},
                    )

    @staticmethod
    def valid_str_value(value: str | None) -> str | None:
        return stripped if (
            value and (stripped := str(value).strip())
        ) else None
