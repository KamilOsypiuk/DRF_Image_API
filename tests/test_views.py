import tempfile
from datetime import timedelta

from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import override_settings

from image_api.models import AccountTier, Image, ExpirationLink, Account
from tests.utils import create_temporary_test_image


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class ImageAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(
            username='test',
            password='testpass')

        cls.basic_tier = AccountTier.objects.create(
            tier="Basic", thumbnail_sizes=['200'], original_link=False, expiration_link=False
        )
        cls.premium_tier = AccountTier.objects.create(
            tier="Premium", thumbnail_sizes=['200, 400'], original_link=True, expiration_link=False
        )
        cls.enterprise_tier = AccountTier.objects.create(
            tier="Enterprise", thumbnail_sizes=['200, 400'], original_link=True, expiration_link=True
        )

        cls.user_account = Account.objects.create(user=cls.user, tier=cls.enterprise_tier)

        cls.test_image = create_temporary_test_image()
        image_file = ContentFile(cls.test_image.getvalue(), cls.test_image.name)
        cls.image = Image.objects.create(image=image_file, account_id=cls.user.pk)

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_can_access_image_create_list_endpoint(self):
        data = {'file': self.test_image}

        response = self.client.post(reverse('image-create-list'), data=data, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_not_authenticated_user_cannot_access_image_create_list_endpoint(self):
        self.client.logout()

        data = {'file': self.test_image}

        response = self.client.post(reverse('image-create-list'), data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_access_user_images_list_endpoint(self):
        response = self.client.get(reverse('user-images-list'))
        self.assertEqual(response.status_code, 200)

    def test_not_authenticated_user_cannot_access_user_images_list_endpoint(self):
        self.client.logout()

        response = self.client.get(reverse('user-images-list'))
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_access_user_image_detail_endpoint(self):
        response = self.client.generic("RETRIEVE", reverse('user-image-detail', kwargs={'image_id': self.image.pk}))
        self.assertEqual(response.status_code, 200)

    def test_not_authenticated_user_cannot_access_user_image_detail_endpoint(self):
        self.client.logout()

        response = self.client.generic("RETRIEVE", reverse('user-image-detail', kwargs={'image_id': self.image.pk}))
        self.assertEqual(response.status_code, 401)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class ExpirationLinkAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(
            username='test',
            password='testpass')

        cls.basic_tier = AccountTier.objects.create(
            tier="Basic", thumbnail_sizes=['200'], original_link=False, expiration_link=False
        )
        cls.premium_tier = AccountTier.objects.create(
            tier="Premium", thumbnail_sizes=['200, 400'], original_link=True, expiration_link=False
        )
        cls.enterprise_tier = AccountTier.objects.create(
            tier="Enterprise", thumbnail_sizes=['200, 400'], original_link=True, expiration_link=True
        )

        cls.test_image = create_temporary_test_image()
        image_file = ContentFile(cls.test_image.getvalue(), cls.test_image.name)
        cls.image = Image.objects.create(image=image_file, account_id=cls.user.pk)

        cls.expiration_link = ExpirationLink.objects.create(image=cls.image,
                                                            expires_at=timezone.now() + timedelta(seconds=30000))

        cls.user_account = Account.objects.create(user_id=cls.user.pk, tier_id=cls.enterprise_tier.pk)

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_can_access_expiration_link_create_endpoint(self):
        data = {"expires_in": 30000}

        response = self.client.post(reverse('expiration-link-create', kwargs={'image_id': self.image.pk}), data=data)
        self.assertEqual(response.status_code, 201)

    def test_not_authenticated_user_cannot_access_expiration_link_create_endpoint(self):
        self.client.logout()

        response = self.client.post(reverse('expiration-link-create', kwargs={'image_id': self.image.pk}))
        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_access_expiration_link_get_endpoint(self):
        response = self.client.get(reverse('expiration-link-get', kwargs={'link_id': self.expiration_link.pk}))
        self.assertEqual(response.status_code, 200)

    def test_not_authenticated_user_cannot_access_expiration_link_get_endpoint(self):
        self.client.logout()

        response = self.client.get(reverse('expiration-link-get', kwargs={'link_id': self.expiration_link.pk}))
        self.assertEqual(response.status_code, 401)
