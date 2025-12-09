from rest_framework import serializers

from .models import Customer
from .models import UserUsage,DailyUsage,MonthlyUsage,MikrotikUser

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
    username=serializers.CharField(source='user.username',read_only=True)
    class Meta:
        model = MonthlyUsage
        fields = ['username', 'year','month', 'total_bytes_used']  

class MikrotikUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MikrotikUser
        fields = ['id', 'username', 'address', 'source', 'raw', 'last_seen', 'quote_bytes', 'email']  # و هر فیلد لازم
        read_only_fields = ['id', 'last_seen']  # last_seen شاید خواندنی باشه 

class FetchUserSerializer(serializers.Serializer):
    username = serializers.CharField()        