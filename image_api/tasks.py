import os
import shutil

from api.celery import app
from PIL import Image as PILImage

from api import settings
from image_api.models import Image, Account


@app.task
def create_thumbnail_sizes(user_id: int, image_path: str, image_id: int) -> list[Image]:
    account = Account.get_or_create_account(user_id=user_id)

    account_tier = account.tier
    image = Image.objects.get(account_id=user_id, id=image_id)

    for thumbnail_size in account_tier.thumbnail_sizes.split(","):

        absolute_path = os.path.join(settings.MEDIA_ROOT, image_path)

        original = PILImage.open(absolute_path)
        newsize = (int(thumbnail_size), int(thumbnail_size))
        resized = original.resize(newsize)

        temp_path = os.path.join(settings.TEMP_ROOT, image_path)

        os.mkdir(temp_path)

        _, extension = os.path.splitext(image_path)
        if extension == '.jpg':
            resized.save(temp_path, format='jpeg')
        resized.save(temp_path)

        thumbnail = Image.objects.create(account_id=image.account.pk, image=resized)

        shutil.rmtree(temp_path)

        image.thumbnail_sizes.add(thumbnail)
    return image.thumbnail_sizes
