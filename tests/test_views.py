from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse

from image_api.models import AccountTier, Image, ExpirationLink, Account
from tests.utils import create_test_image


class ImageAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            username='test',
            password='testpass')

        self.basic_tier = AccountTier.objects.create(
            tier="Basic", thumbnail_sizes=['200'], original_link=False, expiration_link=False
        )
        self.premium_tier = AccountTier.objects.create(
            tier="Premium", thumbnail_sizes=['200, 400'], original_link=True, expiration_link=False
        )
        self.enterprise_tier = AccountTier.objects.create(
            tier="Enterprise", thumbnail_sizes=['200, 400'], original_link=True, expiration_link=True
        )

        self.user_account = Account.objects.create(user=self.user, tier=self.enterprise_tier)
        self.client.force_authenticate(user=self.user)

        image = create_test_image()
        image_file = SimpleUploadedFile(image.name, image.read())
        self.image = Image.objects.create(image=image_file, account_id=self.user.pk)

    def test_authenticated_user_can_access_image_create_list_endpoint(self):
        data = {'file': self.image}

        response = self.client.post(reverse('image-create-list'), data=data, format='multipart')
        self.assertEqual(response.status_code, 201)

    def test_not_authenticated_user_cannot_access_image_create_list_endpoint(self):
        self.client.logout()

        data = {'file': self.image}

        response = self.client.post(reverse('image-create-list'), data=data, format='multipart')
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


class ExpirationLinkAPIViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            username='test',
            password='testpass')

        self.basic_tier = AccountTier.objects.create(
            tier="Basic", thumbnail_sizes=['200'], original_link=False, expiration_link=False
        )
        self.premium_tier = AccountTier.objects.create(
            tier="Premium", thumbnail_sizes=['200, 400'], original_link=True, expiration_link=False
        )
        self.enterprise_tier = AccountTier.objects.create(
            tier="Enterprise", thumbnail_sizes=['200, 400'], original_link=True, expiration_link=True
        )

        image = create_test_image()
        image_file = SimpleUploadedFile(image.name, image.read())
        self.image = Image.objects.create(
            account_id=self.user.pk, image=image_file
        )

        self.expiration_link = ExpirationLink.objects.create(
            image=self.image, expires_at=timezone.now() + timedelta(seconds=30000)
        )

        self.user_account = Account.objects.create(user_id=self.user.pk, tier_id=self.enterprise_tier.pk)
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_can_access_expiration_link_create_endpoint(self):
        response = self.client.post(reverse('expiration-link-create', kwargs={'image_id': self.image.pk}))
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
