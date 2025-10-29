from django.contrib import admin

# Register your models here.
from django.contrib import admin
#from .models import Student
#admin.site.register(Student)
#from .models import Personal
#admin.site.register(Personal)
#from .models import Customer
#admin.site.register(Customer)
#class CustomerAdmin(admin.ModelAdmin):
    #list_display=('name','usage_mb','updated')
#from.models import MikrotikUser,UserUsage
#admin.site.register(MikrotikUser)
#admin.site.register(UserUsage)

from django.urls import path
from django.shortcuts import render
from .models import DailyUsage, MonthlyUsage, UserUsage
from django.contrib import admin
from hello.utils.format_bytes import format_bytes
from django.template.response import TemplateResponse

from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from .models import DailyUsage, MonthlyUsage

#@admin.register(DailyUsage)
#class DailyUsageAdmin(admin.ModelAdmin):
   # list_display = ("user", "date", "total_bytes_used")
from django.contrib import admin
from django import forms
from .models import DailyUsage

class DailyUsageForm(forms.ModelForm):
    total_mb_used = forms.FloatField(label="مصرف (MB)")

    class Meta:
        model = DailyUsage
        fields = ['user', 'date', 'total_mb_used']

    def __init__(self, *args, **kwargs):
        print("uy")
        super().__init__(*args, **kwargs)       
        if getattr(self.instance, 'total_bytes_used', None) not in [None, 0]:
            mb_value = round(self.instance.total_bytes_used / (1024 * 1024), 2)
            self.fields['total_mb_used'].initial = mb_value

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.total_bytes_used = int(self.cleaned_data['total_mb_used'] * 1024 * 1024)
        if commit:
            instance.save()
        return instance

@admin.register(DailyUsage)
class DailyUsageAdmin(admin.ModelAdmin):
    form = DailyUsageForm
    list_display = ['user', 'date', 'total_mb_used_display']

    def total_mb_used_display(self, obj):
        return round(obj.total_bytes_used / (1024 * 1024), 2)
    total_mb_used_display.short_description = "مصرف (MB)"
@admin.register(MonthlyUsage)
class MonthlyUsageAdmin(admin.ModelAdmin):   
    list_display = ("user", "year", "month","total_bytes_used")
        
           
@admin.register(UserUsage)
class UserUsageAdmin(admin.ModelAdmin):
    list_display = ("user", "snapshot_time", "total_bytes")  # 👈 فقط اسم تابع

    


# 📊 داشبورد سفارشی
def usage_dashboard_view(request):
    daily = DailyUsage.objects.select_related("user").order_by("-date")[:10]
    monthly = MonthlyUsage.objects.select_related("user").order_by("-year", "-month")[:10]
    snapshots = UserUsage.objects.order_by("-snapshot_time")[:10]

    context = {
       
    }
    return render(request, "admin/usage_dashboard.html", {
        "daily": daily,
        "monthly": monthly,
        "snapshots": snapshots
 
       })
       

 
class CustomAdminSite(admin.AdminSite):
    site_header = "📊 مدیریت سامانه مصرف کاربران"
    site_title = "مدیریت سامانه"
    index_title = "داشبورد مدیریتی"

    def index(self, request, extra_context=None):
        daily = DailyUsage.objects.order_by('-date')
        monthly = MonthlyUsage.objects.order_by('-year', '-month')
        extra_context = extra_context or {}
        extra_context['daily'] = daily
        extra_context['monthly'] = monthly
        return super().index(request, extra_context)
        
        
admin_site = CustomAdminSite(name='custom_admin')       
from .models import UserUsage, WarnedUser
admin_site.register(UserUsage)
admin_site.register(WarnedUser)
admin_site.register(DailyUsage)
admin_site.register(MonthlyUsage)


#admin .site.unregister(DailyUsage)
from django.contrib import admin
from django import forms
from .models import DailyUsage
