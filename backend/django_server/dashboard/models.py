from django.db import models
from django.contrib.auth.models import User

class Nodes(models.Model):
    mac = models.CharField(primary_key=True, max_length=17)
    ip = models.GenericIPAddressField(protocol='both',default='0.0.0.0')
    port = models.IntegerField(default=0)
    time_stamp = models.IntegerField(default=0)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.mac


class Data(models.Model):
    mac = models.CharField(max_length=17)
    time = models.IntegerField(default=0)
    temp = models.DecimalField(max_digits=10, decimal_places=2)
    hum = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.mac