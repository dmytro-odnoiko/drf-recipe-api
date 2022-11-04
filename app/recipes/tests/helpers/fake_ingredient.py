from core.tests.helpers.faker import faker
from random import randint


class FakeIngredient:
    """Class for generating a fake ingredient with parameters"""
    def __init__(self, fields={}):
        self.amount = fields.get('amount', randint(5, 150))
        self.amount_type = fields.get('amount_type', faker.word())
        self.recipe = fields.get('recipe')
        self.ingredient = fields.get('ingredient')
