# Generated by Django 3.2.15 on 2022-09-19 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_recipe_ingredients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(),
        ),
    ]
