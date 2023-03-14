from django.contrib import admin

# Register your models here.
from home.models import Comments, Category, Advertisement, UserRating

admin.site.register(Comments)
admin.site.register(Category)
admin.site.register(Advertisement)
admin.site.register(UserRating)
