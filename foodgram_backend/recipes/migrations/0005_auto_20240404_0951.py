# Generated by Django 3.2 on 2024-04-04 06:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20240402_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(choices=[('штук', 'штук'), ('кг', 'кгилограмм'), ('гр', 'грамм')], default='гр', max_length=16, verbose_name='Единицы измерения'),
        ),
        migrations.AlterField(
            model_name='recipeingredientvalue',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Количество продукта'),
        ),
        migrations.AddConstraint(
            model_name='recipeingredientvalue',
            constraint=models.UniqueConstraint(fields=('amount', 'ingredients', 'recipe'), name='not_uniq_amount'),
        ),
    ]
