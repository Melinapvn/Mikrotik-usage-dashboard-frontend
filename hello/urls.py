from django.urls import path, include
from . import views 
from hello import views as hello_views
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from hello.api_views import MikrotikUserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

#import view hast dg
from hello.api_views import FetchUserAPIView, MeDailyUsageAPIView, MeMonthlyUsageAPIView, MeFetchUsageAPIView



router = routers.DefaultRouter()
router.register(r'mikrotik-users', MikrotikUserViewSet, basename='mikrotikuser')


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
    path("api/top_consumers_monthly/", views.top_consumers_monthly, name="top-consumers-daily"),
    
    #مسیرهای پنل کاربری
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # endpoint که قبلاً گفتیم؛ نسخه ساده تر:
    path("fetch-user/", FetchUserAPIView.as_view(), name="fetch_user"),  # optional (admin use)

    # endpoints مخصوص user (auth required)
    path("me/daily/", MeDailyUsageAPIView.as_view(), name="me_daily"),
    path("me/monthly/", MeMonthlyUsageAPIView.as_view(), name="me_monthly"),
    path("me/fetch-usage/", MeFetchUsageAPIView.as_view(), name="me_fetch_usage"),
]
    



