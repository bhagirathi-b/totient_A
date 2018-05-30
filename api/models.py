from django.db import models
from django.contrib.auth.models import User


class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    distance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username) + str(self.created_at)

