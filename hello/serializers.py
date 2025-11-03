from rest_framework import serializers

from .models import Customer
from .models import UserUsage,DailyUsage,MonthlyUsage
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields=['id','name','usage_mb']
       

class UserUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUsage
        fields = ['user', 'bytes_in','bytes_out','total_bytes','uptime','snapshot_time','mac_address']    

class DailyUsageSerializer(serializers.ModelSerializer):
    username=serializers.CharField(source='user.username',read_only=True)
    class Meta:    
        model = DailyUsage
        fields = ['username', 'date', 'total_bytes_used']   
        
class MonthlyUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyUsage
        fields = ['user', 'year','month', 'total_bytes_used']        