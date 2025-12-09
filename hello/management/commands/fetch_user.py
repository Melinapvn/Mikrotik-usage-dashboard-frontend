from django.core.management.base import BaseCommand
from hello.utils.mikrotik_fetch import fetch_mikrotik

class Command(BaseCommand):
    help = "Fetch usage for ONE specific user"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)

    def handle(self, *args, **options):
        username = options["username"]

        self.stdout.write(f"Fetching usage for user {username} ...")

        fetch_mikrotik(username=username)

        self.stdout.write(self.style.SUCCESS("DONE"))