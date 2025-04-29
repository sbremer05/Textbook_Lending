from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Collection(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_public = models.BooleanField(default=True)
    allowed_users = models.ManyToManyField(User, blank=True, related_name='allowed_collections')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    # items = models.ManyToManyField(Item, blank=True, related_name='collections')

    def __str__(self):
        return self.title

class CollectionAccessRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied')
    ]

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='access_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collection_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.collection.title} ({self.status})"

class Item(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('checked_out', 'Checked Out'),
        ('repair', 'Being Repaired'),
        ('lost', 'Lost'),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    location = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    collections = models.ManyToManyField(Collection, related_name='items', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items', null=True)

    def save(self, *args, **kwargs):
        # If assigned to any private collection, enforce single collection only
        # private_collections = [c for c in self.collections.all() if not c.is_public]
        # if private_collections and self.collections.count() > 1:
        #     raise ValueError("Item in a private collection can only belong to that one collection.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
  
class Review(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('item', 'user')

# class Rating(models.Model):
#     item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="ratings")
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     value = models.PositiveIntegerField()  # 1–5 stars

# class Comment(models.Model):
#     item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="comments")
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

class BorrowRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('returned', 'Returned')
    ]

    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='borrow_requests')
    patron = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowed_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # New field: due date for when the borrowed item must be returned.
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.patron.username} → {self.item.title} ({self.status})"
