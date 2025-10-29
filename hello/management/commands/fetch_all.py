from django.core.management.base import BaseCommand
from hello.utils.mikrotik_fetch import fetch_mikrotik

class Command(BaseCommand):
    help = "Fetch usage from MikroTik for all users"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting fetch_all...")
        fetch_mikrotik()   # بدون user_id یعنی همه رو بیاره
        self.stdout.write(self.style.SUCCESS("✅ Finished fetch_all"))