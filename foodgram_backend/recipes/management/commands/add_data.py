import csv
# import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = ('Импорт данных из csv файла в БД.'
            'Перед импортом данных необходимо удалить БД.')

    def handle(self, *args, **options):
        self.stdout.write('Добавление базы данных!')
        # relative_path = "data"
        # absolute_path = os.path.abspath(relative_path)
        absolute_path = '/data'

        CSV_DATA_AND_MODELS = (
            ('ingredients.csv', Ingredient),
        )

        for file_name, models in CSV_DATA_AND_MODELS:
            with open(
                f'{absolute_path}/{file_name}', 'r', encoding='utf-8'
            ) as csvfile:
                data = csv.DictReader(csvfile)
                list_to_add_in_db = []
                for row in data:
                    list_to_add_in_db.append(models(**row))
                models.objects.bulk_create(list_to_add_in_db)
        self.stdout.write('База данных добавлена!')
