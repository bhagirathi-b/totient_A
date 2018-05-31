from django.db import models
from django.contrib.auth.models import User

from math import sin, cos, sqrt, atan2, radians
R = 6373.0


def distance(from_latitude, from_longitude, to_latitude, to_longitude):
    from_latitude = radians(float(from_latitude))
    from_longitude = radians(float(from_longitude))
    to_latitude = radians(float(to_latitude))
    to_longitude = radians(float(to_longitude))

    latitude_difference = from_latitude - to_latitude
    longitude_difference = from_longitude - to_longitude

    a = sin(latitude_difference / 2) ** 2 + cos(from_latitude) * cos(to_latitude) * sin(longitude_difference / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


class GeoLocation(models.Model):
    long = models.FloatField()
    lat = models.FloatField()


class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    froml = models.ForeignKey(GeoLocation, related_name="froml", on_delete=models.CASCADE, null=True, blank=True)
    tol = models.ForeignKey(GeoLocation, related_name="tol", on_delete=models.CASCADE, null=True, blank=True)
    distance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username) + str(self.created_at)

    @property
    def from_location(self):
        return "Longitude : {} - Latitude: {}".format(self.froml.long, self.froml.lat)

    @from_location.setter
    def from_location(self, from_location):
        _from_long = float(from_location.get('long'))
        _from_lat = float(from_location.get('lat'))
        geo = GeoLocation.objects.create(long=_from_long, lat=_from_lat)
        self.froml = geo

    @property
    def to_location(self):
        return "Longitude : {} - Latitude: {}".format(self.tol.long, self.tol.lat)

    @to_location.setter
    def to_location(self, to_location):
        _to_long = float(to_location.get('long'))
        _to_lat = float(to_location.get('lat'))
        geo = GeoLocation.objects.create(long=_to_long, lat=_to_lat)
        self.tol = geo

    @property
    def distance(self):
        """
        Calculate distance
        :return:
        """
        return distance(self.froml.lat, self.froml.long, self.tol.lat, self.tol.long)