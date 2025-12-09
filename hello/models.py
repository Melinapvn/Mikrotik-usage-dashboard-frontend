from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models
# Create your models here.

class Student(models.Model):
    name=models.CharField(max_length=100)
    age=models.IntegerField()
    grade=models.CharField(max_length=10)  

    def __str__(self) :
        return self.name

class Personal(models.Model):
    name=models.CharField(max_length=100)
    ip=models.IntegerField()
    masraf=models.CharField(max_length=10)
 

    def __str__(self) :
        return self.name

class Customer(models.Model):
    name=models.CharField(max_length=100)
    usage_mb=models.FloatField(default=0)
    updated=models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name



class MikrotikUser(models.Model):
    
    username = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    
    address = models.GenericIPAddressField(blank=True, null=True)
        
    source = models.CharField(max_length=50, blank=True, null=True)     
    raw = models.JSONField(default=dict)  
    
    last_seen = models.DateTimeField(default=timezone.now)
    
    quote_bytes = models.BigIntegerField(default=6000)
    
    last_warned = models.DateField(null=True, blank=True)
    
    email = models.EmailField(default="thebestworld21@gmail.com")
  

    def __str__(self):
        return self.username or self.order or "unknown"


class UserUsage(models.Model):

    user = models.ForeignKey(MikrotikUser, 
    on_delete=models.CASCADE, related_name="usages")

    bytes_in = models.BigIntegerField(default=0)

    bytes_out = models.BigIntegerField(default=0)

    total_bytes = models.BigIntegerField(default=0)
    
    snapshot_time = models.DateTimeField(default=timezone.now)

    uptime = models.DurationField(default=timedelta())
    
    mac_address=models.CharField(max_length=50, null=True, blank=True)

        
    

    
    def __str__(self):

        return f"{self.user}"

class DailyUsage(models.Model):

    user = models.ForeignKey(MikrotikUser, on_delete=models.CASCADE)

    date = models.DateField()

    total_bytes_used = models.BigIntegerField()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique_user_date')
    ]
    
    def __str__(self):
        return f"{self.user} - {self.date}:{self.total_bytes_used}"
    
    
class MonthlyUsage(models.Model):
    user = models.ForeignKey(MikrotikUser, on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    total_bytes_used = models.BigIntegerField(default=0)

    class Meta:
        unique_together = ("user", "year", "month")

    def _str_(self):
        return f"{self.user.username} - {self.year}/{self.month} : {self.total_bytes_used} bytes"   

class WarnedUser(models.Model):
    user = models.ForeignKey(MikrotikUser, on_delete=models.CASCADE)
    warnes_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

class Notofication(models.Model) :
    user=models.ForeignKey(MikrotikUser, on_delete=models.CASCADE)   
    message=models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    sent = models.BooleanField(default=False)
    type = models.CharField(max_length=20, default="email")
    
    def __str__(self):
        return f"{self.user.username}-{self.message[:30]}"
   

