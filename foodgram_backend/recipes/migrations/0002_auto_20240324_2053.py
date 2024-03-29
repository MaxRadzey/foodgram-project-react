# Generated by Django 3.2 on 2024-03-24 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='time',
            new_name='cooking_time',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='tag',
            new_name='tags',
        ),
        migrations.RenameField(
            model_name='recipeingredientvalue',
            old_name='value',
            new_name='amount',
        ),
        migrations.RemoveField(
            model_name='ingredient',
            name='unit',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(choices=[('GR', 'грамм'), ('KG', 'кгилограмм'), ('SHT', 'штук')], default='GR', max_length=16, verbose_name='Единицы измерения'),
        ),
    ]
