#django files
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

#packages
from PIL import Image

class User(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\d{11}$',
        message="Phone number must be exactly 11 digits."
    )

    ROLE_CHOICES = [
        ('CUSTOMER', 'مشتری'),
        ('SELLER', 'آرایشگر'),
        ('MANAGER', 'مدیر')

    ]
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11, unique=True, validators=[phone_regex], blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    image = models.ImageField(default='profile_pics/default.png', upload_to='profile_pics', blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image and self.image.name != 'default.png':
            img_path = self.image.path

            img = Image.open(img_path)

            img.thumbnail((300, 300))

            img.save(img_path, optimize=True, quality=85)

    def __str__(self):
        return self.username
