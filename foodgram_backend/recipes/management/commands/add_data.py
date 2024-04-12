import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = ('Импорт данных из csv файла в БД.'
            'Перед импортом данных необходимо удалить БД.')

    def handle(self, *args, **options):
        self.stdout.write('Добавление базы данных!')
        absolute_path = 'data'
        file_name = 'ingredients.csv'

        try:
            with open(
                f'{absolute_path}/{file_name}', 'r', encoding='utf-8'
            ) as csvfile:
                data = csv.DictReader(csvfile, ['name', 'measurement_unit'])
                list_to_add_in_db = []
                for row in data:
                    list_to_add_in_db.append(Ingredient(
                        name=row['name'],
                        measurement_unit=row['measurement_unit'],
                    ))
                Ingredient.objects.bulk_create(list_to_add_in_db)
            self.stdout.write('База данных добавлена!')
        except FileNotFoundError:
            self.stdout.write(f'Файл {file_name} не найден!')
