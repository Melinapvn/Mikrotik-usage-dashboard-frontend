from django.urls import re_path
from . import consumers
from hello.consumers import DailyUsageConsumer

websocket_urlpatterns = [

    re_path(r"ws/daily_usage/$", consumers.DailyUsageConsumer.as_asgi()),
    re_path(r"ws/top_daily/$", consumers.TopDailyConsumer.as_asgi()),
    re_path(r"ws/monthly_usage/$", consumers.MonthlyUsageConsumer.as_asgi()),
    re_path(r"ws/top_monthly/$", consumers.TopMonthlyConsumer.as_asgi()),
    #re_path(r'ws/usage/$', consumers.UsageConsumer.as_asgi()),
    
    #re_path(r"ws/monthly/$", consumers.MonthlyUsageConsumer.as_asgi()),
    #re_path(r"ws/live/$", consumers.LiveUsageConsumer.as_asgi()),   # برای مصرف لحظه‌ای
    #re_path(r"ws/users/$", consumers.UserConsumer.as_asgi()),       # برای لیست کاربران (اختیاری)
    #re_path(r"ws/test/$", consumers.TestConsumer.as_asgi()),
    
    
]
