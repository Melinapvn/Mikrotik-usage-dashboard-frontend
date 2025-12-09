from django.utils import timezone
from datetime import datetime, time
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from datetime import datetime, time
from librouteros import connect
from hello.models import MikrotikUser, UserUsage, DailyUsage
from datetime import timedelta

def calculate_daily_usage(snapshot_date=None):
    print("shuru")
    if not snapshot_date:
        snapshot_date = timezone.now().date()

    # شروع و پایان روز
    start = datetime.combine(snapshot_date, time.min, tzinfo=timezone.get_current_timezone())
    end = datetime.combine(snapshot_date, time.max, tzinfo=timezone.get_current_timezone())

    daily_totals = {}

    users = MikrotikUser.objects.all()   # 👈 همه‌ی یوزرها

    for user in users:                   # 👈 حلقه روی هر یوزر
        snapshots = UserUsage.objects.filter(
            user=user,
            snapshot_time__range=(start, end)
        ).order_by("snapshot_time")

        if not snapshots.exists():
            continue   # 👈 پرش به یوزر بعدی

        total_usage = 0
        prev_snapshot = snapshots.first()
        before_reset_usage = prev_snapshot.total_bytes

        for snap in snapshots[1:]:
            if snap.uptime < prev_snapshot.uptime:
                # ریست شناسایی شد
                total_usage += before_reset_usage
            prev_snapshot = snap
            before_reset_usage = snap.total_bytes

        # آخرین بخش رو هم اضافه کنیم
        total_usage += snapshots.last().total_bytes

        daily_usage = total_usage
        daily_totals[user.username] = daily_usage

        DailyUsage.objects.update_or_create(
            user=user,
            date=snapshot_date,
            total_bytes_used=daily_usage,

        )

    return daily_totals