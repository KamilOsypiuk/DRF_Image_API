from uuid import UUID

from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from image_api.exceptions import ServiceException
from image_api.models import Image
from image_api.serializers import ExpirationLinkOutputSerializer, ImageSerializer, ManyImagesOutputSerializer, \
    ExpirationImageOutputSerializer
from image_api.services import ImageService, ExpirationLinkService
from image_api.tasks import create_thumbnail_sizes


class ImageApiView(GenericAPIView, RetrieveModelMixin):
    queryset = Image.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = ImageSerializer
    http_method_names = ['post', 'get', 'retrieve']

    def post(self, request: Request) -> Response:
        """Upload image"""
        service = ImageService(request)
        file = request.FILES["file"]
        serializer = self.serializer_class(data={'image': file})
        serializer.is_valid(raise_exception=True)
        try:
            image = service.create_image(file=file)
            create_thumbnail_sizes.delay(user_id=request.user.pk, image_path=image.image.path, image_id=image.pk)
            return Response('Image successfully uploaded', status=status.HTTP_201_CREATED)
        except (ServiceException, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request: Request) -> Response:
        """List all images associated with user"""
        service = ImageService(request=request)
        try:
            images = service.return_image_sizes_based_on_tier()

            serializer = ManyImagesOutputSerializer(data={'images': images})
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            return Response(data, status=status.HTTP_200_OK)
        except (ServiceException, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Retrieve one user image"""
        service = ImageService(request=request)
        try:
            image_id = self.kwargs["image_id"]
            service.validate_access_to_image(image_id=image_id)
            images = service.return_specific_image_sizes_based_on_tier(image_id=image_id)

            serializer = ManyImagesOutputSerializer(data={'images': images})
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            return Response(data, status=status.HTTP_200_OK)
        except (ServiceException, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class ExpirationLinkApiView(GenericAPIView):
    queryset = Image.objects.all()
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post', 'get']

    def post(self, request: Request, image_id: int) -> Response:
        """Create expiration link for image"""
        service = ExpirationLinkService(request=request)
        try:
            expiration_link = service.create_expiration_link(image_id=image_id)
            serializer = ExpirationLinkOutputSerializer(data={'url': expiration_link.url})
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            return Response(data, status=status.HTTP_201_CREATED)
        except (ServiceException, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request: Request, link_id: UUID) -> Response:
        """Get image from expiration link"""
        service = ExpirationLinkService(request=request)
        try:
            expiration_link = service.get_image_from_expiration_link(link_id=link_id)
            serializer = ExpirationImageOutputSerializer(data=expiration_link)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            return Response(data, status=status.HTTP_200_OK)
        except (ServiceException, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
