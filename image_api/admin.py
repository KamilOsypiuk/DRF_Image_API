from django.contrib import admin

# Register your models here.
from image_api.models import Image, Account, AccountTier, ExpirationLink

admin.site.register(Image)
admin.site.register(Account)
admin.site.register(AccountTier)
admin.site.register(ExpirationLink)