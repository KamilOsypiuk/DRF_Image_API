import os
from celery import shared_task

from PIL import Image as PILImage

from image_api.models import Image, Account


@shared_task
def create_thumbnail_sizes(user_id: int, image_path: str, image_id: int) -> None:
    account = Account.get_or_create_account(user_id=user_id)

    account_tier = account.tier
    image = Image.objects.get(account_id=user_id, id=image_id)

    original = PILImage.open(image_path)

    for thumbnail_size in account_tier.thumbnail_sizes.split(", "):
        newsize = (int(thumbnail_size), int(thumbnail_size))
        resized = original.resize(size=newsize)

        root, ext = os.path.splitext(image_path)

        media_path = f"{root}_{thumbnail_size}x{thumbnail_size}{ext}"
        resized.save(media_path)

        _, relative_path = root.split("\\media\\")
        thumbnail_path = f"{relative_path}_{thumbnail_size}x{thumbnail_size}{ext}"

        thumbnail = Image.objects.create(account_id=image.account.pk, image=thumbnail_path)

        image.thumbnails.add(thumbnail)
