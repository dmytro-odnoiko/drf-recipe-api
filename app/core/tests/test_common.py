from unittest.mock import patch

from django.test import SimpleTestCase

from core.tests.helpers.faker import faker

from core.utils import image_filepath


class CommonTests(SimpleTestCase):

    @patch('core.utils.uuid.uuid4')
    def test_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = faker.word()
        mock_uuid.return_value = uuid
        instance = faker.word()
        file_path = image_filepath(instance, 'example.jpg')

        self.assertEqual(file_path, f'uploads/{repr(instance)}/{uuid}.jpg')
