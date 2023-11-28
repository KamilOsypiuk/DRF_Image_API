from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request

import magic

from image_api.exceptions import ServiceException
from image_api.models import Image, Account, ExpirationLink
from image_api.serializers import ExpirationLinkInputSerializer


class ImageService:
    def __init__(self, request: Request):
        self.request = request
        self.user = request.user

    @staticmethod
    def __validate_file_extension(file) -> bool:
        allowed_extension = ["jpg", "jpeg", "png"]
        file_type = magic.from_buffer(file.read(2048))
        extension = file_type.split(' ')
        if extension[0] not in allowed_extension + [ext.upper() for ext in allowed_extension]:
            raise ServiceException(f"Invalid file extension. Allowed extensions are: {allowed_extension}")
        return True

    def validate_access_to_image(self, image_id: int) -> bool:
        image = get_object_or_404(Image, id=image_id)
        if image.account == self.user.pk or self.user.is_staff or self.user.is_superuser:
            return True
        raise ServiceException('Access to this image was denied')

    @transaction.atomic
    def create_image(self, file) -> Image:
        self.__validate_file_extension(file=file)
        return Image.objects.create(account_id=self.user.pk, image=file, original_photo=True)

    def return_specific_image_sizes_based_on_tier(self, image_id: int) -> list:
        account = Account.get_or_create_account(user_id=self.user.pk)
        account_tier = account.tier

        image = get_object_or_404(Image, id=image_id, account=self.user.pk)
        thumbnails = Image.objects.filter(thumbnail_sizes=image_id)
        image_data_list = []

        if account_tier.original_link:
            image_data_list.append({
                'size': f"{image.width}x{image.height}",
                'url': image.url,
            })

        thumbnail_data_list = [
            {
                'size': f"{thumbnail.width}x{thumbnail.height}",
                'url': thumbnail.url,
            }
            for thumbnail in thumbnails
        ]
        image_data_list.extend(thumbnail_data_list)

        return image_data_list

    def return_image_sizes_based_on_tier(self) -> list[dict]:
        account = Account.get_or_create_account(user_id=self.user.pk)

        account_tier = account.tier

        images = Image.objects.filter(account=self.user.pk)

        if not account_tier.original_link:
            thumbnail_data_list = [
                {
                    'size': f"{image.width}x{image.height}",
                    'url': image.url,
                }
                for image in images.filter(original_photo=False)
            ]
            return thumbnail_data_list

        image_data_list = [
            {'size': f"{image.width}x{image.height}",
             'url': image.url,
             }
            for image in images
        ]

        return image_data_list


class ExpirationLinkService:
    def __init__(self, request: Request):
        self.user = request.user
        self.request = request
        self.serializer = ExpirationLinkInputSerializer(data=self.request.data)

    def __validate_access_to_create_link(self, user_id: int) -> bool:
        account = Account.get_or_create_account(user_id=user_id)

        account_tier = account.tier

        if not account_tier.expiration_link:
            raise ServiceException(
                "You don't have permission to access this feature. Consider upgrading your membership")

        return True

    def create_expiration_link(self, image_id: int) -> ExpirationLink:
        self.__validate_access_to_create_link(user_id=self.user.pk)
        ImageService(self.request).validate_access_to_image(image_id=image_id)
        self.serializer.is_valid(raise_exception=True)
        data = self.serializer.validated_data
        image = get_object_or_404(Image, id=image_id, account=self.user.pk)

        return ExpirationLink.objects.create(image=image,
                                             expires_at=timezone.now() + timedelta(seconds=data['expires_in']))

    def __validate_expiration_link(self, link: ExpirationLink) -> bool:
        if link.expires_at < timezone.now():
            link.delete()
            raise ValidationError('This link expired')
        return True

    def get_image_from_expiration_link(self, link_id) -> Image:
        link = get_object_or_404(ExpirationLink, id=link_id)
        self.__validate_expiration_link(link=link)
        return link.image
