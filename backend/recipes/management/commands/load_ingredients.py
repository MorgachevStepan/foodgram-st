import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Loads ingredients from JSON file into the database'
    DATA_DIR = os.path.join(settings.BASE_DIR, 'data')
    FILE_PATH = os.path.join(DATA_DIR, 'ingredients.json')

    def handle(self, *args, **options):
        if not os.path.exists(self.FILE_PATH):
            self.stdout.write(
                self.style.ERROR(f'File not found: {self.FILE_PATH}. Current BASE_DIR is {settings.BASE_DIR}'))
            return

        self.stdout.write(f'Loading ingredients from {self.FILE_PATH}...')

        try:
            with open(self.FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found (during open): {self.FILE_PATH}'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Error decoding JSON file.'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {e}'))
            return

        ingredients_to_create = []
        loaded_count = 0
        skipped_count = 0
        existing_names = set(Ingredient.objects.values_list('name', flat=True))  # Чтобы не дублировать

        for item in data:
            name = item.get('name')
            measurement_unit = item.get('measurement_unit')

            if not name or not measurement_unit:
                self.stdout.write(self.style.WARNING(f'Skipping invalid item (missing name or unit): {item}'))
                skipped_count += 1
                continue

            if name in existing_names:
                skipped_count += 1
                continue

            ingredients_to_create.append(
                Ingredient(name=name, measurement_unit=measurement_unit)
            )
            loaded_count += 1

        if not ingredients_to_create:
            self.stdout.write(self.style.SUCCESS('No new ingredients to load.'))
            if skipped_count > 0:
                self.stdout.write(self.style.WARNING(f'Skipped {skipped_count} items (invalid or existing).'))
            return

        try:
            Ingredient.objects.bulk_create(
                ingredients_to_create)
            self.stdout.write(self.style.SUCCESS(
                f'Successfully loaded {loaded_count} new ingredients.'
            ))
            if skipped_count > 0:
                self.stdout.write(self.style.WARNING(f'Skipped {skipped_count} items (invalid or existing).'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during bulk create: {e}'))