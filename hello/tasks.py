from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

def send_daily_update():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "daily_usage",  # همون group_name که تو Consumer تعریف کردی
        {
            "type": "send_update",  # متد Consumer که پیام رو می‌فرسته
            "payload": {"message": "این یه پیام تستیه از سرور!"}
        }
        )