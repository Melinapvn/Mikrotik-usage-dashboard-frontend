from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DailyUsage, MonthlyUsage
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import time
import datetime
from datetime import date

# DailyUsage (create/update)
@receiver(post_save, sender=DailyUsage)
def daily_usage_saved(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    payload = {
        "action": action,
        "model": "daily",
        "id": instance.id,
        "user": instance.user.username,
        "date":str(instance.date),
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
        # ارسال به چارت روزانه
        async_to_sync(channel_layer.group_send)(
            "daily_group",   # ← گروه درست
            {
                "type": "send_update",
                "payload": payload,   # ← کلید درست
            }
        )

        # آپدیت لیست top users
        top_users = get_top_users_direct()
        async_to_sync(channel_layer.group_send)(
            "top_daily_group",
            {
                "type": "send_top_daily",
                "data": {
                    "model": "top_daily",
                    "users": top_users
                }
            }
        )

def send_top_daily_update(top_users):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "top_daily_group",
        {
            "type": "send_top_daily",
            "data": {
                "model": "top_daily",
                "users": top_users
            }
        }
    )

def get_top_users_direct():
    today = datetime.date.today()

    return list(
        DailyUsage.objects.filter(date=today)
        .order_by("-total_bytes_used")[:5]
        .values(
            "user__username",
            "total_bytes_used"
        )
    )

@receiver(post_save, sender=DailyUsage)
def update_top_daily_on_save(sender, instance, **kwargs):
    top_users = get_top_users_direct()
    print("📊 Top 5 recalculated on save:", top_users)
    send_top_daily_update(top_users)


@receiver(post_delete, sender=DailyUsage)
def update_top_daily_on_delete(sender, instance, **kwargs):
    top_users = get_top_users_direct()
    print("📉 Top 5 recalculated on delete:", top_users)
    send_top_daily_update(top_users)
    
# 🔥 ارسال داده ماهانه به Live WebSocket
def _send_monthly_usage_update():
    today = date.today()

    data = (
        MonthlyUsage.objects
        .filter(year=today.year, month=today.month)
        .values("user__username", "total_bytes_used","year","month")
        .order_by("-total_bytes_used")
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "monthly_usage_group",
        {
            "type": "send_monthly_update",
            "data": {
                "model": "monthly_usage",
                "records": list(data)
            }
        }
    )

# 🔥 ارسال top 5 مصرف ماهانه
def _send_top_monthly_update():
    today = date.today()

    top = list(
        MonthlyUsage.objects
        .filter(year=today.year, month=today.month)
        .values("user__username", "total_bytes_used")
        .order_by("-total_bytes_used")[:5]
    )

    # تبدیل به کلیدهای قابل فهم برای frontend
    top_users = [
        {"user__username": t["user__username"], "total_bytes_used": t["total_bytes_used"]}
        for t in top
    ]

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "top_monthly_group",
        {
            "type": "send_top_monthly",
            "data": {
                "model": "top_monthly",
                "users": top_users
            }
        }
    )
# 🔔 سیگنال نهایی
@receiver(post_save, sender=MonthlyUsage)
def update_monthly_ws(sender, instance, **kwargs):
    _send_monthly_usage_update()
    _send_top_monthly_update()    