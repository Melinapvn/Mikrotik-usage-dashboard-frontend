from django.utils import timezone
from datetime import datetime, time, timedelta
from hello.models import MikrotikUser, UserUsage, DailyUsage, MonthlyUsage, UserUsage
from django.db.models import Sum
import logging

def calculate_daily_usage(user=None, snapshot_date=None):
    print("shoru masrafe roozaneh... ...")

    if not snapshot_date:
        snapshot_date = timezone.now().date()

    # شروع و پایان روز جاری
    start = datetime.combine(snapshot_date, time.min, tzinfo=timezone.get_current_timezone())
    end = datetime.combine(snapshot_date, time.max, tzinfo=timezone.get_current_timezone())
    print(start)
    print(end)

    daily_totals = {}

    if user:
        users = [user]
        print(f"📌 mohasebeh faqat baraye yek karbar {user.username}")
    else:
        users = MikrotikUser.objects.all()
      #  print("📌 mohaseberh barayr tamamekarbaran")
    #users = MikrotikUser.objects.all() 
    #print(users.username)
    for user in users:
        # تمام snapshot های امروز برای این کاربر
        snapshots = UserUsage.objects.filter(
            user=user,
            snapshot_time__date__gte=start,snapshot_time__date__lte=end,)        
        if not snapshots.exists():
            continue

        # تمام MAC های منحصربه‌فرد کاربر در آن روز
        mac_list = snapshots.values_list("mac_address", flat=True).distinct()
        #mac_list = snapshots.values_list('mac_address',flat=True)
        mac_list_values = list(mac_list)  # تبدیل QuerySet به لیست واقعی

        if len(mac_list_values) > 0:
            print("مقدار اول:", mac_list_values[0])
        else:
            print("mac_list خالی است")

        if len(mac_list_values) > 1:
            print("مقدار دوم:", mac_list_values[1])
        else:
            print("mac_list فقط یک مقدار دارد یا خالی است")
        #print(f"user:{user},MACS Found:{mac_list[0]}")
        #print(f"user:{user},MACS Found:{mac_list[1]}")

        user_total = 0
        for mac in mac_list:
            mac_snaps = snapshots.filter(mac_address=mac)
            mac_snaps = list(mac_snaps)
            if not mac_snaps:
                continue

            prev_uptime = mac_snaps[0].uptime
            daily_total = mac_snaps[0].total_bytes

            for snap in mac_snaps[1:]:
                if snap.uptime < prev_uptime:
                    daily_total += snap.total_bytes
                else:
                    daily_total = snap.total_bytes
                prev_uptime = snap.uptime

            print(f"🔸 {user.username} ({mac}) →masraf roozaneh MAC: {daily_total}")
            user_total += daily_total
            print(user_total)

        # مجموع همه‌ی MACها برای کاربر
        daily_totals[user.username] = user_total
        obj, created = DailyUsage.objects.update_or_create(user=user,date=snapshot_date,defaults={"total_bytes_used": daily_total})
        if created:
            print(f"new record{user.username}")
        else:
            print(f"update{user.username}")        
        print(f"{user.username} → مصرف روزانه: {daily_total}")
        print(f"✅ mojmoo nahayi {user.username}: {user_total}\n")

    print("🎯 محاسبه‌ی مصرف روزانه تمام شد.")    
    return daily_totals
 

def calculate_daily_usagee(user=None, snapshot_date=None):
    print("شروع محاسبه مصرف روزانه ...")
    if not snapshot_date:
        snapshot_date = timezone.now().date()
    
    # شروع و پایان روز
    start = datetime.combine(snapshot_date, time.min, tzinfo=timezone.get_current_timezone())
    print()
    end = datetime.combine(snapshot_date, time.max, tzinfo=timezone.get_current_timezone())

    daily_totals = {}
    if user:
        print("one_user")
        users=[user]
    else:
        print("all_users")
        users = MikrotikUser.objects.all()    
    for user in users:
        print(user)
        snapshots = UserUsage.objects.filter(
            user=user,
            snapshot_time__range=(start, end)
        ).order_by("snapshot_time")

        if not snapshots.exists():
            continue

        snapshots = list(snapshots)  # برای راحتی در دسترسی به first/last
        prev_uptime = snapshots[0].uptime
        daily_total = snapshots[0].total_bytes
        print(f"prev_totaol_byte={daily_total}")
        print(f"prev_uptime={prev_uptime}")
        
        

        for snap in snapshots[1:]:
            if snap.uptime < prev_uptime:                
                daily_total += snap.total_bytes                                
            else:               
                daily_total = snap.total_bytes                                  
            prev_uptime = snap.uptime 
            print(prev_uptime)
            prev_total_bytes =snap.total_bytes 
            
        # ذخیره در dict و جدول دیتابیس
        daily_totals[user.username] = daily_total
       # DailyUsage.objects.update_or_create(
           # user=user,
            #date=snapshot_date,
           # total_bytes_used=daily_total
        #)
        obj, created = DailyUsage.objects.update_or_create(user=user,date=snapshot_date,defaults={"total_bytes_used": daily_total})
        if created:
            print(f"new record{user.username}")
        else:
            print(f"update{user.username}")        
        print(f"{user.username} → مصرف روزانه: {daily_total}")
  
    
def calculate_monthly_usage_for_user_both(user=None, as_of_date=None):
    """محاسبه incremental: جمع روزهای قبل از امروز + مصرف امروز (از آخرین snapshot)."""
    if as_of_date is None:
        as_of_date = timezone.now().date()
    first_of_month = as_of_date.replace(day=1)

    # اگر یوزر داده شده → فقط همون یوزر
    if user:
        users = [user]
        print("mohasebeh baraye yek mah")
    else:
        # اگر یوزر داده نشده → همه یوزرهایی که در این ماه DailyUsage دارند
        users = MikrotikUser.objects.filter(id__in=UserUsage.objects.filter(date__range=(first_of_month, as_of_date)).values_list("user_id", flat=True).distinct())
    results = {}
    for u in users:
        # روزانه رو هم محاسبه می‌کنیم (برای پر شدن DailyUsage امروز)
        result = calculate_daily_usage(user=u)
        print(f"calculate_daily_usage={result}")

        # جمع کل روزهای ماه (از اول ماه تا امروز)
        totaldays_of_month = DailyUsage.objects.filter(
            user=u, date__range=(first_of_month, as_of_date)
        ).aggregate(total=Sum('total_bytes_used'))['total'] or 0

        print(f"totaldays_of_month={totaldays_of_month}")

        # ذخیره یا آپدیت در MonthlyUsage
        monthly, created = MonthlyUsage.objects.update_or_create(
            user=u,
            year=as_of_date.year,
            month=as_of_date.month,
            defaults={"total_bytes_used": totaldays_of_month}
        )

        if created:
            print(f"✅ رکورد جدید ساخته شد: {monthly}")
        else:
            print(f"🔄 رکورد آپدیت شد: {monthly}")

        results[getattr(u, "username", u)] = totaldays_of_month

    return totaldays_of_month    

def calculate_monthly_usage_for_user(user, as_of_date=None):

    """محاسبه incremental: جمع روزهای قبل از امروز + مصرف امروز (از آخرین snapshot)."""
    if as_of_date is None:
        as_of_date = timezone.now().date()
        first_of_month = as_of_date.replace(day=1)
    result=calculate_daily_usage(user=user)
    print(f"calculate_daily_usage={result}")
    #prev_days = DailyUsage.objects.filter(user=user, date__range=(first_of_month, as_of_date- timedelta(days=1))).aggregate(total=Sum('total_bytes_used'))['total'] or 0
    totaldays_of_month = DailyUsage.objects.filter(user=user, date__range=(first_of_month, as_of_date)).aggregate(total=Sum('total_bytes_used'))['total'] or 0
    print(f"totaldays_of_month={totaldays_of_month}") 
    # مصرف امروز از آخرین snapshot
    #last_today = DailyUsage.objects.filter(user=user, date=as_of_date).values_list("total_bytes_used", flat=True).first()
    #print(f"last_today={last_today}")
    #today_bytes = last_today.total_bytes_used if last_today else 0
    #prev_days(f"today_bytes={today_bytes}")
    print (f" used_monthly={totaldays_of_month}")
    monthly, created = MonthlyUsage.objects.update_or_create(
        user=user,
        year=as_of_date.year,
        month=as_of_date.month,
        defaults={"total_bytes_used": totaldays_of_month}
    )

    if created:
        print(f"✅ رکورد جدید ساخته شد: {monthly}")
    else:
        print(f"🔄 رکورد آپدیت شد: {monthly}")
    return totaldays_of_month
    
    



def calculate_monthly_usage(year=None, month=None):  
    now = timezone.now()
    if year is None:
        year=now.year
    if month is None:    
        month = now.month

        # شروع و پایان ماه
    start = datetime(year, month, 1, tzinfo=timezone.get_current_timezone())
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=timezone.get_current_timezone()) - timedelta(seconds=1)
    else:
        end = datetime(year, month + 1, 1, tzinfo=timezone.get_current_timezone()) - timedelta(seconds=1)
        
    monthly_total={} 
    users=MikrotikUser.objects.all()    

    for user in MikrotikUser.objects.all():
            # جمع کل از DailyUsage
        calculate_daily_usage(user=user)    
        daily_usage = DailyUsage.objects.filter(
            user=user,
            date__range=(start.date(), end.date()))
        total_bytes=sum(d.total_bytes_used for d in daily_usage)

            # ذخیره یا آپدیت
        MonthlyUsage.objects.update_or_create(
            user=user,
            year=year,
            month=month,
            total_bytes_used=total_bytes
            )
        monthly_total[user.username]=total_bytes
    return monthly_total   
            
            #self.stdout.write(
            #f"{user.username} | {year}-{month:02d} | {total / (1024*1024*1024):.2f} GB"
            # python manage.py fetch_mikrotik_daily_monthly_usage    