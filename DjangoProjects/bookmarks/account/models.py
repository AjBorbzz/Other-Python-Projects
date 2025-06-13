from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE) # force the deletion of the related profile
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', # stores the relative path to the file in the related database field.
                              blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'