from django.db import models
from django.contrib.auth.models import User
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from django.db.models.signals import pre_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('driver', 'Driver'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Produce(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity_kg = models.FloatField()
    pickup_location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)


class Transport(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    route_start_lat = models.FloatField()
    route_start_lng = models.FloatField()
    route_end_lat = models.FloatField()
    route_end_lng = models.FloatField()
    capacity_total = models.FloatField()
    capacity_used = models.FloatField(default=0)
    scheduled_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    route_start_address = models.CharField(
        max_length=255, blank=True, null=True)
    route_end_address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Transport by {self.driver.username} from {self.route_start_address} to {self.route_end_address}"


geolocator = Nominatim(user_agent="agripool-app")


def reverse_geocode(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language='en')
        return location.address if location else f"{lat}, {lon}"
    except GeocoderTimedOut:
        return f"{lat}, {lon}"


def cache_transport_addresses(sender, instance, **kwargs):
    if not instance.route_start_address:
        instance.route_start_address = reverse_geocode(
            instance.route_start_lat, instance.route_start_lng)
    if not instance.route_end_address:
        instance.route_end_address = reverse_geocode(
            instance.route_end_lat, instance.route_end_lng)


@receiver(pre_save, sender=Transport)
def pre_save_transport(sender, instance, **kwargs):
    cache_transport_addresses(sender, instance)
