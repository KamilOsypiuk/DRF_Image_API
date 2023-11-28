from io import BytesIO

from PIL import Image


def create_temporary_test_image():
    image_file = BytesIO()
    image = Image.new('RGB', (100, 100), 'white')
    image.save(image_file, 'PNG')
    image_file.name = "test_image.png"
    image_file.seek(0)
    return image_file
