from django.contrib import admin

# Register your models here.
from home.models import Comments, Category, Advertisement

admin.site.register(Comments)
admin.site.register(Category)
admin.site.register(Advertisement)
