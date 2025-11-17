import os
import django
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# تنظیم محیط Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

def send_test_message():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "daily_usage",
        {
            "type": "send_update",  # نام متدی که تو consumer داری
            "payload": {"message": "test update from script"}
        }
    )
    print("✅ Test message sent to daily_usage group")

if __name__ == "_main_":
    send_test_message()