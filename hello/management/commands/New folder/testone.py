# hello/management/commands/testone.py
from django.core.management.base import BaseCommand
from hello.utils import calculate_daily_usage   # مسیر درست تابع رو بذار

class Command(BaseCommand):
    help = "تست تابع calculate_daily_usage"

    def handle(self, *args, **options):
        result = calculate_daily_usage()
        self.stdout.write(self.style.SUCCESS("نتیجه تست:"))
        self.stdout.write(str(result))