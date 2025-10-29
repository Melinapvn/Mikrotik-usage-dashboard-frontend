from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from librouteros import connect
from hello.models import MikrotikUser, UserUsage
from datetime import timedelta
import re


# ✅ اضافه کردن داده‌های Mock
MOCK_MODE = True  
  

MOCK_DATA = [
    {
        'user': 'test1',
        'address': '192.168.1.10',
        'mac-address': 'AA:BB:CC:DD:EE:01',
        'bytes-in': '100',
        'bytes-out': '400',
        'uptime' : '5h15m30s',
    },
    {
        'user': 'test2',
        'address': '192.168.1.11',
        'mac-address': 'AA:BB:CC:DD:EE:02',
        'bytes-in': '200',
        'bytes-out': '200',
        'uptime' : '5h15m30s',
    },
{
        'user': 'ali',
        'address': '192.168.1.12',
        'mac-address': 'AA:BB:CC:DD:EE:03',
        'bytes-in': '500',
        'bytes-out': '1300',
        'uptime' : '6h15m30s'
    },
]


def safe_duration(value: str) -> timedelta:
    """Convert MikroTik uptime string (e.g. '2h15m30s') to timedelta"""
    if not value:
        return timedelta()

    days = hours = minutes = seconds = 0
    match = re.findall(r'(\d+)([dhms])', value)
    for num, unit in match:
        num = int(num)
        if unit == 'd':
            days = num
        elif unit == 'h':
            hours = num
        elif unit == 'm':
            minutes = num
        elif unit == 's':
            seconds = num
    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

def safe_int(x):
    try:
        return int(x) if x is not None else 0
    except Exception:
        return 0


def normalize_item(item):
    """تبدیل داده‌های MikroTik به دیکشنری str"""
    out = {}
    for k, v in item.items():
        key = k.decode() if isinstance(k, bytes) else k
        val = v.decode() if isinstance(v, bytes) else v
        out[key] = val
    return out


class Command(BaseCommand):
    help = 'Fetch users from MikroTik (hotspot/ppp) and save/update DB + usage history'

    def add_arguments(self, parser):
        parser.add_argument('--host', required=False)
        parser.add_argument('--username', required=False)
        parser.add_argument('--password', required=False)
        parser.add_argument('--port', type=int, default=8728)
        parser.add_argument('--ssl', action='store_true', dest='use_ssl')

    def handle(self, *args, **options):
        # ✅ چک کردن MOCK_MODE
        if MOCK_MODE:
            self.stdout.write(self.style.SUCCESS('Running in MOCK MODE'))
            
            self.process_mock_data()
            check_and_handle_quota()
            return

        # کد اصلی برای اتصال به MikroTik
        host = options.get('host') or getattr(settings, 'MIKROTIK', {}).get('HOST')
        username = options.get('username') or getattr(settings, 'MIKROTIK', {}).get('USERNAME')
        password = options.get('password') or getattr(settings, 'MIKROTIK', {}).get('PASSWORD')
        port = options.get('port') or getattr(settings, 'MIKROTIK', {}).get('PORT', 8728)
        use_ssl = options.get('use_ssl') or getattr(settings, 'MIKROTIK', {}).get('USE_SSL', False)

        if not host or not username or password is None:
            self.stderr.write(self.style.ERROR(
                'Provide --host, --username, --password or set MIKROTIK in settings.py'
            ))
            return

        try:
            with connect(host=host, username=username, password=password, port=port, use_ssl=use_ssl) as api:
                self.stdout.write(self.style.SUCCESS(f'Connected to MikroTik {host}'))
                sources = [
                    ('hotspot', '/ip/hotspot/active/print'),
                    ('ppp', '/ppp/active/print'),
                ]
                total = 0

                for source_name, path in sources:
                    try:
                        items = list(api(path))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Cannot read {path}: {e}'))
                        items = []

                    total += self.process_items(items, source_name)

                self.stdout.write(self.style.SUCCESS(f'Finished. {total} records saved/updated.'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error connecting to MikroTik: {e}'))

    def process_mock_data(self):
        """پردازش داده‌های Mock"""
        total = self.process_items(MOCK_DATA, 'mock')
        self.stdout.write(self.style.SUCCESS(f'Mock data processed. {total} records saved/updated.'))

    def process_items(self, items, source_name):
        """پردازش آیتم‌ها و ذخیره در دیتابیس"""
        total = 0
        
        if not items:
            return total

        for item in items:
            d = normalize_item(item)

            username_val = d.get('user') or d.get('name') or d.get('caller-id') or d.get('account')
            address = d.get('address')
            mac = d.get('mac-address') or d.get('mac')

            bytes_in = safe_int(d.get('bytes-in') or d.get('rx-byte') or 0)
            bytes_out = safe_int(d.get('bytes-out') or d.get('tx-byte') or 0)
            total_bytes = bytes_in + bytes_out
            uptime= safe_duration(d.get('uptime')) 

            lookup = {}
            if username_val:
                lookup['username'] = username_val
            if address:
                lookup['address'] = address
            if not lookup:
                continue

            defaults = {
                'mac_address': mac,
                'bytes_in': bytes_in,
                'bytes_out': bytes_out,
                'total_bytes': total_bytes,
                'source': source_name,
                'raw': d,
                'last_seen': timezone.now(),
                'uptime': uptime,
            }

            user_obj, created = MikrotikUser.objects.update_or_create(**lookup , defaults={'mac_address': mac,
                'bytes_in': bytes_in,
                'bytes_out': bytes_out,
                'total_bytes': total_bytes,
                'source': source_name,
                'raw': d,
                'last_seen': timezone.now(),
                }
            )

            UserUsage.objects.create(
                user=user_obj,
                bytes_in=bytes_in,
                bytes_out=bytes_out,
                total_bytes=total_bytes,
                snapshot_time=timezone.now(),
                uptime= uptime,                 
            )

            total += 1

        return total