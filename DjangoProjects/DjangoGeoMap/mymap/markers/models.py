from django.contrib.gis.db import models


class Marker(models.Model):
    name = models.CharField()
    location = models.PointField()

    def __str__(self):
        return str(self.name)