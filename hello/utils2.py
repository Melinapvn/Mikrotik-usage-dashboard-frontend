from django.utils import timezone
from datetime import datetime, time
from hello.models import MikrotikUser, UserUsage, DailyUsage

def calculate_daily_usage(snapshot_date=None):
    print("شروع محاسبه مصرف روزانه")
    
    if not snapshot_date:
        snapshot_date = timezone.now().date()

    # شروع و پایان روز
    start = datetime.combine(snapshot_date, time.min, tzinfo=timezone.get_current_timezone())
    end = datetime.combine(snapshot_date, time.max, tzinfo=timezone.get_current_timezone())

    daily_totals = {}

    users = MikrotikUser.objects.all()  # همه‌ی یوزرها

    for user in users:
        snapshots = UserUsage.objects.filter(
            user=user,
            snapshot_time__range=(start, end)
        ).order_by("snapshot_time")

        if not snapshots.exists():
            continue

        prev_uptime = None
        daily_total = 0
        session_total=0

        for snap in snapshots:
            if prev_uptime is None:
                session_total = snap.total_bytes
            elif snap.uptime < prev_uptime:
                # session ادامه داره
                daily_total += session_total
                session_total=snap.total_bytes
            else:
                # ریست شده
                session_total =snap.total_bytes

            prev_uptime = snap.uptime
        
        daily_total +=session_total
        daily_totals[user.username]=daily_total
        

        # ثبت یا آپدیت رکورد روزانه در DailyUsage
        DailyUsage.objects.update_or_create(
            user=user,
            date=snapshot_date,
            total_bytes_used=daily_total
        )


    print("محاسبه مصرف روزانه تکمیل شد")
    return daily_totals