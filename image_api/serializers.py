from rest_framework import serializers

from rest_framework.fields import ImageField

from image_api.models import Image


class ImageSerializer(serializers.Serializer):
    image = ImageField()


class ImageOutputSerializer(serializers.Serializer):
    size = serializers.CharField()
    url = serializers.CharField()


class ManyImagesOutputSerializer(serializers.Serializer):
    images = ImageOutputSerializer(many=True)


class ExpirationLinkInputSerializer(serializers.Serializer):
    expires_in = serializers.IntegerField(min_value=300, max_value=30000,
                                          error_messages={
                                              'min_value': 'Expires_in must be greater than or equal to 300 seconds.',
                                              'max_value': 'Expires_in must be less than or equal to 30000 seconds.',
                                          }
                                          )


class ExpirationLinkOutputSerializer(serializers.Serializer):
    url = serializers.URLField()

class ExpirationImageOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("image",)
        read_only_fields = fields
