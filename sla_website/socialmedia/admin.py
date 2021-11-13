from django.contrib import admin

# Register your models here.
from .models import Acts, Post

admin.site.register(Acts)
admin.site.register(Post)

