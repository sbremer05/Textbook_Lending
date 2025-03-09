from django.db import models

# Create your models here.
class Item(models.Model):
    title = models.CharField(max_length=255)
    identifier = models.CharField(max_length=100, unique=True)  # ISBN, barcode, etc.
    status = models.CharField(max_length=50, choices=[('available', 'Available'), ('borrowed', 'Borrowed')])
    location = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="item_images/", null=True, blank=True)  # ✅ S3 image upload

    def __str__(self):
        return self.title