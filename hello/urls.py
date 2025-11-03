from django.urls import path
from . import views 
from hello import views as hello_views
from django.urls import path, include
from rest_framework import routers





router = routers.DefaultRouter()



urlpatterns = [
    path('api/', include(router.urls)),
    path('api/customers/', views.customer_api, name='customer_api'),
    path('report/', views.report_dashboard, name='report_dashboard'),
    path('api/daily-usage/', views.daily_usage_api, name='daily_usage_api'),
    path('api/daily-calculate/', views.daily_calculate_api, name='daily_usage_api'),
    path('api/Monthly-calculate/', views.monthly_calculate_api, name='monthly_usage_api'),
    path('api/export/daily/pdf/', views.export_daily_usage_pdf, name='export_daily_usage_pdf'),
    path('api/export/daily/csv/', views.export_daily_usage_csv, name='export_daily_usage_csv'),
    path('api/export/daily/excel/', views.export_daily_usage_excel, name='export_daily_usage_excel'),    
    path("api/top-consumers-daily/", views.top_consumers_daily, name="top-consumers-daily"),
    
]


