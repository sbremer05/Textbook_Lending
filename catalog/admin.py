from django.contrib import admin
from .models import Item, Collection, Comment, Rating, BorrowRequest


# Register your models here.
admin.site.register(Item)
admin.site.register(Collection)
admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(BorrowRequest)