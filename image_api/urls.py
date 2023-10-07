
from django.urls import path
from image_api.views import ImageApiView, ExpirationLinkApiView

urlpatterns = [
    path('images/', ImageApiView.as_view(), name='image-create-list'),
    path('images/', ImageApiView.as_view(), name='user-images-list'),
    path('images/<int:image_id>/', ImageApiView.as_view(),
         name='user-image-detail'),
    path('images/<int:image_id>/expiration_link/',
         ExpirationLinkApiView.as_view(), name='expiration-link-create'),
    path('images/expiration_link/<uuid:link_id>/',
         ExpirationLinkApiView.as_view(), name='expiration-link-get')
]
