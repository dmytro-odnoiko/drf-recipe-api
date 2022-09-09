import uuid
import os


def image_filepath(instance, filename):
    """Generate filepath for image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', repr(instance), filename)
