from django.core.management.base import BaseCommand
from hello.utils.mikrotik_fetch import fetch_mikrotik
from hello.utils.quote import check_and_handle_quota
from hello.models import MikrotikUser
from hello.utils.aggregate import calculate_daily_usage,calculate_monthly_usage_for_user_both

class Command(BaseCommand):
    help = "Run MikroTik related tasks (fetch, check, warned, ...)"

    def add_arguments(self, parser):
        parser.add_argument("--mode", type=str, choices=["fetch_all", "check_warned_users","daily","monthly"], default="fetch")

    def handle(self, *args, **opts):
        if opts["mode"] == "fetch_all":
            #for u in MikrotikUser.objects.all():
            #fetch_mikrotik()
            from .fetch_all import Command as FetchAllCommand
            FetchAllCommand().handle()
            self.stdout.write('start fetching usesr')
        elif opts["mode"] == "check_warned_users":
            from .check_warned_users import Command as FetchWarnedUsers
            FetchWarnedUsers().handle()
            self.stdout.write('checked quota for warned users')
            #for u in MikroTikUser.objects.all():
                #check_and_handle_quota(u)
        elif opts["mode"] == "daily": 
            self.stdout.write('calculating daily usage...') 
            calculate_daily_usage()
            self.stdout.write(self.style.SUCCESS("FINISH DAILY USAGE"))
        elif opts["mode"] == "monthly": 
            self.stdout.write('calculating monthly usage...') 
            calculate_monthly_usage_for_user_both()
            self.stdout.write(self.style.SUCCESS("FINISH monthly USAGE"))    
            
                
