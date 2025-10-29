from django.core.mail import send_mail
from django.conf import settings
from hello.models import Notofication

def send_notification(user, message, notify_type="email"):
    """ایجاد نوتیف و ارسال ایمیل در صورت نیاز"""
    print('hi from notify')
    notif = Notofication.objects.create(
        user=user,
        message=message,
        type=notify_type
    )
    print(f"notify_type={notify_type}")
    if notify_type == "email":
        print('mail')
        send_mail(
            subject="about net",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        notif.sent = False
        notif.save()

    return notif