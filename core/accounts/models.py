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
        ('STAFF', 'آرایشگر'),
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
class HomeImage(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="images/")
    def save(self, *args, **kwargs):
        if self.pk:
            orig = HomeImage.objects.filter(pk=self.pk).first()
            orig_image = orig.image if orig else None
        else:
            orig_image = None

        super().save(*args, **kwargs)

        if self.image and (not orig_image or self.image.name != orig_image.name):
            self.resize_image()

    def resize_image(self):
        image_path = self.image.path
        try:
            with Image.open(image_path) as img:
                target_size = (1080, 945)
                resized_img = img.resize(target_size, Image.LANCZOS)
                format = img.format or 'JPEG'
                resized_img.save(image_path, format=format, quality=95)
        except Exception as e:
            print(f"Error resizing image: {e}")

