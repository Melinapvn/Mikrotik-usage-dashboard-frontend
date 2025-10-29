from librouteros import connect
from django.conf import settings

def enforce_on_mikrotik(user):
    """قطع دسترسی کاربر از طریق MikroTik"""
    try:
        with connect(
            host=settings.MIKROTIK["HOST"],
            username=settings.MIKROTIK["USERNAME"],
            password=settings.MIKROTIK["PASSWORD"],
            port=settings.MIKROTIK.get("PORT", 8728),
        ) as api:
            # 👇 برای PPP
            for u in api("/ppp/secret/print"):
                if u.get("name") == user.username:
                    api("/ppp/secret/set", {"disabled": "yes", ".id": u[".id"]})
                    break

            # 👇 برای Hotspot
            for u in api("/ip/hotspot/user/print"):
                if u.get("name") == user.username:
                    api("/ip/hotspot/user/set", {"disabled": "yes", ".id": u[".id"]})
                    break

            print(f"✅ User {user.username} disabled on MikroTik")

    except Exception as e:
        print(f"❌ Error disabling user {user.username}: {e}")