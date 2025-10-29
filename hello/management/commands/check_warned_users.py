from django.core.management.base import BaseCommand
from hello.utils.mikrotik_fetch import fetch_mikrotik
from hello.models import WarnedUser,Notofication
from hello.utils.mikrotik_fetch import fetch_mikrotik

from django.conf import settings

class Command(BaseCommand):
    help = "Fetch active sessions from MikroTik"

    def add_arguments(self, parser):
        parser.add_argument("--host", required=False)
        parser.add_argument("--username", required=False)
        parser.add_argument("--password", required=False)
        parser.add_argument("--port", type=int, default=8728)
        parser.add_argument("--ssl", action="store_true", dest="use_ssl")

    def handle(self, *args, **options):
        try:
            #total = fetch_mikrotik(options)
            #self.stdout.write(self.style.SUCCESS(f"✅ Finished. {total} records saved/updated."))
            warned=WarnedUser.objects.filter(active=True)
            if not warned.exists():
                self.stdout.write("no warned users")
                return
                for w in warned:
                    user=w.user 
                    try:
                        fetch_mikrotik(username=user.username)
                    except Exception as e:
                        self.stderr.write(f"fetch error for {user.username}:{e}")
                        #continue   
                   # used = calculate_monthly_usage_for_user(user)
                    #quota = user.quota_bytes or 0
                    #pct = (used / quota) * 100 if quota else 0
                   # if pct >= 100:
                      #  Notification.objects.create(user=user, message="مصرف شما به 100% رسید؛ اینترنت محدود شد.")
                       # w.active = False
                       # w.save(update_fields=['active'])
                # اختیاری: enforce_on_router(user)
                       # self.stdout.write(f"{user.username}: 100% -> enforced")
                    #elif pct >= 85:
                    #    Notification.objects.create(user=user, message=f"مصرف شما {pct:.1f}% سهمیه است.")
                    #    self.stdout.write(f"{user.username}: {pct:.1f}% warned")    
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error: {e}"))