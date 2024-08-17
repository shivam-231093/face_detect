from django.db import models


class Image(models.Model):
    id = models.AutoField(primary_key=True)  # Explicitly define AutoField
    image_file = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    firebase_url = models.URLField(max_length=200, blank=True, null=True)
