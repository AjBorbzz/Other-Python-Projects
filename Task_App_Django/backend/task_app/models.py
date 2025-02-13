from django.db import models

class Tasks(models.Model):
    title = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.title