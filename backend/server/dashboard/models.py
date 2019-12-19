from django.db import models
from django.contrib.auth.models import User

class Current_status(models.Model):
    current_online = models.IntegerField(default=0)
    current_time = models.DateTimeField()
    current_temp = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    current_hum = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return (self.current_online, self.current_time, self.current_temp, self.current_hum)


class Node(models.Model):
    mac = models.CharField(primary_key=True, max_length=17)
    ip = models.GenericIPAddressField(protocol='both',default='0.0.0.0')
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.mac


class Data(models.Model):
    id = models.AutoField(primary_key=True)
    mac = models.CharField(max_length=17)
    time = models.IntegerField(default=0)
    temp = models.DecimalField(max_digits=10, decimal_places=2)
    hum = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.mac