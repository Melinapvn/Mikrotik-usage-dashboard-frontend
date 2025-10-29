from django.urls import path
from . import views 
from hello import views as hello_views
from django.urls import path, include
from rest_framework import routers



router = routers.DefaultRouter()



urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.customer_list, name='home'),
    path('about/',views.about),
    path('api/customers/', views.customer_api, name='customer_api'),
    path('report/', views.report_dashboard, name='report_dashboard'),
    path('api/daily-usage/', views.daily_usage_api, name='daily_usage_api'),
    path('api/daily-calculate/', views.daily_calculate_api, name='daily_usage_api'),
    #path('api/usage/', hello_views.usage_data, name='usage_data'),
    

]
