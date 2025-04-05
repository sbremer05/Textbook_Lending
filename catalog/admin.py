from django.contrib import admin
from .models import Item, Collection, Review, BorrowRequest


# Register your models here.
admin.site.register(Item)
admin.site.register(Collection)
admin.site.register(Review),
admin.site.register(BorrowRequest)