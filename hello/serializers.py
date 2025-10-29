from rest_framework import serializers

from .models import Customer
from .models import UserUsage,DailyUsage
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields=['id','name','usage_mb']
       

class UserUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUsage
        fields = ['user', 'bytes_in','bytes_out','total_bytes','uptime','snapshot_time','mac_address']    

class DailyUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyUsage
        fields = ['user', 'date', 'total_bytes_used']       