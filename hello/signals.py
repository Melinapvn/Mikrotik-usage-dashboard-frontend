from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DailyUsage, MonthlyUsage
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import time

# DailyUsage (create/update)
@receiver(post_save, sender=DailyUsage)
def daily_usage_saved(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    payload = {
        "action": action,
        "model": "daily",
        "id": instance.id,
        "user": instance.user.username,
        "total_bytes_used": instance.total_bytes_used,
        "snapshot_time": str(instance.snapshot_time) if hasattr(instance, "snapshot_time") else None
    }
    print("payload dar signal",payload)

    # ✅ مقدار channel_layer اینجا گرفته میشه، نه در بالای فایل
    channel_layer = get_channel_layer()
    print("channel layer",channel_layer)
    if channel_layer:
        print("sending ws update:",payload)
        time.sleep(1)
        async_to_sync(channel_layer.group_send)(
            "daily_usage",
            {"type":"send_update","payload": payload}
        )
    print("sending to websocket",payload)    


# DailyUsage deleted
@receiver(post_delete, sender=DailyUsage)
def daily_usage_deleted(sender, instance, **kwargs):
    payload = {
        "action": "deleted",
        "model": "daily",
        "id": instance.id,
        "user": instance.user.username,
    }

    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            "daily_usage",
            {"type": "send_update", "data": payload}
        )

# MonthlyUsage
