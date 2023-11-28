from uuid import uuid4

from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models import ImageField

from image_api.utils import user_directory_path

from decouple import config

# Create your models here.


class AccountTier(models.Model):
    tier = models.CharField(default="Basic", max_length=150, unique=True)
    thumbnail_sizes = models.CharField(max_length=150, default=None, null=True, blank=True,
                                       validators=[validate_comma_separated_integer_list])
    original_link = models.BooleanField(default=False)
    expiration_link = models.BooleanField(default=False)

    class Meta:
        db_table = "account_tier"


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tier = models.ForeignKey(AccountTier, on_delete=models.CASCADE, default=1, null=False)

    @classmethod
    def get_or_create_account(cls, user_id: int) -> 'Account':
        try:
            account = cls.objects.get(user_id=user_id)
        except cls.DoesNotExist:
            account = cls.objects.create(user_id=user_id, tier_id=1)
        return account

    class Meta:
        db_table = "account"


class Image(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    original_photo = models.BooleanField(default=False)
    image = ImageField(upload_to=user_directory_path,
                       width_field="width",
                       height_field="height")
    thumbnail_sizes = models.ForeignKey('self', default=None, null=True,
                                        on_delete=models.CASCADE, related_name="thumbnails")

    @property
    def url(self):
        return f"{config('root_domain')}media/images/{self.image.name}"

    class Meta:
        db_table = "image"


class ExpirationLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()

    @property
    def url(self):
        return f"{config('root_domain')}images/expiration_link/{self.id}"

    class Meta:
        db_table = "expiration_link"
