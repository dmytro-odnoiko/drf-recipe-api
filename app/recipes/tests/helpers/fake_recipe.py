from decimal import Decimal
from core.tests.helpers.faker import faker
from random import randint, randrange


class FakeRecipe:
    """Class for generating a fake recipe with parameters"""
    def __init__(self, fields={},):
        self.title = fields.get('title', faker.sentence())
        self.time_minutes = fields.get('time_minutes', randint(5, 150))
        self.price = fields.get(
            'price',
            round(Decimal(randrange(500, 10000)/100), 1),
        )
        self.description = fields.get('description', faker.paragraph())
        self.link = fields.get('link', faker.url())
