from hello.utils.notify import send_notification
from hello.utils.aggregate import calculate_monthly_usage_for_user_both
from hello.utils.notify import send_notification
from hello.models import WarnedUser,MikrotikUser
from django.utils import timezone
import logging
logger=logging.getLogger(__name__)
import traceback
            

def check_and_handle_quota(user=None):
    
    print("TRACE: called from:")
    #traceback.print_stack()   
    print("start check")
    if user:
        users = [user]
    else:
        users = MikrotikUser.objects.all()
    for user in users:
        if not user.quote_bytes:
            print("donot quata")
        used = calculate_monthly_usage_for_user_both(user)        
    print(f"used={used}")
    quota = user.quote_bytes
    print(f"quota={quota}")
    pct = (used / quota) * 100 if quota else 0
    logger.info(f"DEBUG: pct={pct}, used={used},quota={quota}")
    print (pct)
    today = timezone.now().date()
    if 85 <= pct < 100:
        # اگر هنوز وارد WarnedUser نشده، اضافه کن
        print('start darsad')
        #logger.info("Condition matched: 85<=pct<100")
        w, created = WarnedUser.objects.get_or_create(user=user)
        #logger.debug(f"WarnedUser {w} created={created}")
        if not w.active:
            print("parcham")
            w.active = True; w.save(update_fields=['active'])
        # نوتیف هر روز فقط یک بار: از last_warned استفاده کن
        if not w.warnes_at or w.warnes_at.date() != timezone.now().date():
            print("email 85")
            send_notification(user,"شما 85 درصد اینترنت خود را مصزف کرده اید","email")
            w.warnes_at = today
            w.save(update_fields=['warnes_at'])
    elif pct >= 100:
        # نوتیف نهایی و غیرفعال کردن monitored state
        print('start darsad bala')
        #logger.info("Condition matched: pct>=100")
        send_notification(user,"اینترنت شما به پایان رسیده است و متاسقانه محدودیت هایی برای شما در نظر گرفته خواهد شد","email")
        WarnedUser.objects.update_or_create(user=user, defaults={'active': False})
        # enforce_on_router(user)
        #user.delete() delkhah
    else:
       
    # اگر قبلاً توی WarnedUser بوده و حالا مصرف کم شده، غیر فعالش کن/////in qesmat baraye dataye dastiye khodam neveshte shode
        w = WarnedUser.objects.filter(user=user, active=True).first()
        if w:
            w.delete()
            
            print(f"❌ کاربر {user} از WarnedUser خارج شد (pct={pct})")  
    # enforce_on_router(user)