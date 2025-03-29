from django.contrib import admin
from .models import Item, Collection, Comment, Rating


# Register your models here.
admin.site.register(Item)
admin.site.register(Collection)
admin.site.register(Comment)
admin.site.register(Rating)