"""Helpers for testing user API"""
from core.tests.helpers.faker import faker


class FakeUser:
    """Class for generating a fake user with parameters"""
    def __init__(self, fields={}, pass_parms={'length': 5}):
        self.name = fields.get('name', faker.first_name())
        self.email = fields.get('email', faker.email())
        self.password = fields.get('password', faker.password(**pass_parms))

    def as_dict(self, name_needed=True):
        user_dict = {
            'email': self.email,
            'password': self.password,
        }
        if name_needed:
            user_dict.update({'name': self.name, })
        return user_dict
