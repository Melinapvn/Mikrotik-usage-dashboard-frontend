from librouteros import connect
from django.utils import timezone
from django.conf import settings
from hello.utils.quote import check_and_handle_quota
from datetime import timedelta
from hello.models import MikrotikUser, UserUsage
import re
import ast 
from django.contrib.auth .models import User


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
    
#MOCK_MODE = getattr(settings, "MOCK_MODE", False)
#MOCK_DATA = getattr(settings, "MOCK_DATA", [])

MOCK_MODE = True  
  
MOCK_DATA1 = [
    {
        'user': 'test3',
        'address': '192.168.1.10',
        'mac-address': 'AA:BB:CC:DD:EE:01',
        'bytes-in': '3000',
        'bytes-out': '2000',       
        'uptime' : '20h15m30s',
    },
     {
        'user': 'test3',
        'address': '192.168.1.10',
        'mac-address': 'AA:BB:CC:DD:EE:02',
        'bytes-in': '3000',
        'bytes-out': '2000',       
        'uptime' : '2h15m30s',
    },
     {
        'user': 'test3',
        'address': '192.168.1.10',
        'mac-address': 'AA:BB:CC:DD:EE:02',
        'bytes-in': '2000',
        'bytes-out': '4000',       
        'uptime' : '5h15m30s',
    },  
       {
        'user': 'test3',
        'address': '192.168.1.10',
        'mac-address': 'AA:BB:CC:DD:EE:01',
        'bytes-in': '3000',
        'bytes-out': '1000',       
        'uptime' : '10h15m30s',
    },
]
MOCK_DATA = [
  
     {
        'user': 'test1',
        'address': '192.168.1.10',
        'mac-address': 'AA:BB:CC:DD:EE:02',
        'bytes-in': '2000',
        'bytes-out': '40000',       
        'uptime' : '5h15m30s',
    },
    {
        'user': 'test2',
        'address': '192.168.1.11',
        'mac-address': 'AA:BB:CC:DD:EE:02',
        'bytes-in': '1500',
        'bytes-out': '300',
        'uptime' : '2h15m30s',
    },
{
        'user': 'ali',
        'address': '192.168.1.12',
        'mac-address': 'AA:BB:CC:DD:EE:03',
        'bytes-in': '5000000000',
        'bytes-out': '7000000000',
        'uptime' : '9h15m30s'
    },
    {
        'user': 'soraya',
        'address': '192.168.1.10',
        'mac-address': 'AA:BB:CC:DD:EE:01',
        'bytes-in': '500',
        'bytes-out': '500',       
        'uptime' : '8h15m30s',
    },
     {
        'user': 'hamed',
        'address': '192.168.1.10',
        'mac-address': 'AA:BB:CC:DD:EE:01',
        'bytes-in': '1000',
        'bytes-out': '1000',       
        'uptime' : '1h15m30s',
    },
     {
        'user': 'melisssa',
        'address': '192.168.1.10',
        'mac-address': 'AA:BB:CC:DD:EE:01',
        'bytes-in': '1',
        'bytes-out': '1000',       
        'uptime' : '13h15m30s',
    },
    
   
    
            {
        'user': 'Saba',
        'address': '192.168.1.10',
        'mac-address': 'AA:BB:CC:DD:EE:01',
        'bytes-in': '1000',
        'bytes-out': '100',       
        'uptime' : '15h15m30s',
    },
           {
        'user': 'talash',
        'address': '192.168.1.10',
        'mac-address': 'AA:BB:CC:DD:EE:01',
        'bytes-in': '20',
        'bytes-out': '800',       
        'uptime' : '15h15m30s',
    },
      {
        'user': 'hemmat',
        'address': '192.168.1.10',
        'mac-address': 'AA:BB:CC:DD:EE:01',
        'bytes-in': '20',
        'bytes-out': '8000',       
        'uptime' : '15h15m30s',
    },
          {
        'user': 'Iran',
        'address': '192.168.1.10',
        'mac-address': 'AA:BB:CC:DD:EE:01',
        'bytes-in': '20',
        'bytes-out': '8000',       
        'uptime' : '15h15m30s',
    },
    
]

def fetch_mikrotik(options=None, username=None, mock_mode=True):
    """دریافت داده از MikroTik و ذخیره در DB"""
   
    if MOCK_MODE:
        
        process_items(MOCK_DATA, "mock")
        print("end process")
        print(username)
        if username:
            user_obj = MikrotikUser.objects.get(username=username)
            check_and_handle_quota(user=user_obj)
        else:        
            check_and_handle_quota()
        return
        
        

    host = options.get("host") or settings.MIKROTIK.get("HOST")
    username = options.get("username") or settings.MIKROTIK.get("USERNAME")
    password = options.get("password") or settings.MIKROTIK.get("PASSWORD")
    port = options.get("port") or settings.MIKROTIK.get("PORT", 8728)
    use_ssl = options.get("use_ssl") or settings.MIKROTIK.get("USE_SSL", False)

    if not host or not username or password is None:
        raise ValueError("Missing MikroTik connection parameters")

    
    with connect(host=host, username=username, password=password, port=port, use_ssl=use_ssl) as api:
        sources = [
            ("hotspot", "/ip/hotspot/active/print"),
            ("ppp", "/ppp/active/print"),
        ]
        total=0
        for source_name, path in sources:
            try:
                items = list(api(path))
            except Exception as e:
                print(f"⚠️ Cannot read {path}: {e}")
                items = []
            total+=process_items(items, source_name)   
            



def process_items(items, source_name):
    """پردازش آیتم‌ها و ذخیره در دیتابیس"""
    
    total = 0
    for item in items:
        d = normalize_item(item)
        print(d)

        username_val = d.get("user") or d.get("name") or d.get("caller-id") or d.get("account")
        address = d.get("address")
        mac = d.get("mac-address") or d.get("mac")
        print("bytes-in=",d.get("bytes-in"))
        bytes_in = safe_int(d.get("bytes-in") or d.get("rx-byte") or 0)
        
        bytes_out = safe_int(d.get("bytes-out"))
        total_bytes = bytes_in + bytes_out
        print(f"bytes-in={bytes_in}, bytes-out={bytes_out},total-bytes={total_bytes}")
        uptime = safe_duration(d.get("uptime"))

        lookup = {}
        if username_val:
            lookup["username"] = username_val
        #if address:
            #lookup["mac_address"] = mac
        if not lookup:
            continue

        user_obj, created = MikrotikUser.objects.update_or_create(
            **lookup,
            defaults={
                #"mac_address": mac,
                #"bytes_in": bytes_in,
                #"bytes_out": bytes_out,
                #"total_bytes": total_bytes,
                "source": source_name,
                "raw": json.loads(d) if isinstance(d, str) else d,
                "last_seen": timezone.now(),
                
            },
        
        )
        django_user, django_created = User.objects.get_or_create(username=user_obj.username)
        if django_created:
    # اگر تازه ساخته شد، پسورد اولیه بذار
            django_user.set_password("123456")  # میتونی پسورد دیگه هم بذاری
            django_user.save()
    


        UserUsage.objects.create(
            user=user_obj,
            bytes_in=bytes_in,
            bytes_out=bytes_out,
            total_bytes=total_bytes,
            snapshot_time=timezone.now(),
            uptime=uptime,
            mac_address=mac,
        )
        
        total += 1               
    return total
