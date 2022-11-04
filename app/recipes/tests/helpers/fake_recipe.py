from decimal import Decimal
from random import randint, randrange

from core.tests.helpers.faker import faker


class FakeRecipe:
    """Class for generating a fake recipe with parameters"""
    def __init__(
            self,
            user=None,
            fields={},
            with_tags=False,
            with_ingredients=False,
            add_fields_count=2):
        self.title = fields.get('title', faker.sentence())
        self.time_minutes = fields.get('time_minutes', randint(5, 150))
        self.price = fields.get(
            'price',
            round(Decimal(randrange(500, 10000)/100), 1),
        )
        self.description = fields.get('description', faker.paragraph())
        self.link = fields.get('link', faker.url())
        if user:
            self.user = user
        if with_tags:
            self.tags = fields.get(
                'tags',
                [{'name': faker.word()} for i in range(add_fields_count)],
            )
        if with_ingredients:
            self.ingredientrecipe_set = fields.get(
                'ingredients',
                [
                    {
                        'ingredient': {'name': faker.word()},
                        'amount': randint(5, 150),
                        'amount_type': faker.word()
                    } for i in range(add_fields_count)
                ]
            )
