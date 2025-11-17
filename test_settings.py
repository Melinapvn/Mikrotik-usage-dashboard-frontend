import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from django.conf import settings
print(settings.CHANNEL_LAYERS)