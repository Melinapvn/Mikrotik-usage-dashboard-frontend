from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserUsage
from .serializers import UserUsageSerializer
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from hello.models import DailyUsage,MonthlyUsage,UserUsage,MikrotikUser,WarnedUser
# Create your views here.
from django.http import HttpResponse 
from .models import Customer
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer
from .serializers import CustomerSerializer
from .serializers import DailyUsageSerializer

 
@api_view(['GET']) 
def daily_usage_api(request):
    data = UserUsage.objects.all().order_by('-snapshot_time')
    serializer = UserUsageSerializer(data, many=True)
    return Response(serializer.data) 

@api_view(['GET'])
def daily_calculate_api(request):
    data = DailyUsage.objects.all().order_by('-date')
    serializer = DailyUsageSerializer(data, many=True)
    return Response(serializer.data)    

def customer_list(request):
    customers=Customer.objects.all().order_by('name')
    return render(request, 'hello/customer.html',{'customers':customers})

#def home(request):
   #return HttpResponse("Hello world")
def about(request):
    return HttpResponse("samaneye")
def home(request):
 
    return render(request, 'hello/home.html')




@api_view(['GET'])

def customer_api(request):

    customers = Customer.objects.all()

    serializer = CustomerSerializer(customers, many=True)

    return Response(serializer.data)
    
def report_dashboard(request):
    snapshots=UserUsage.objects.select_related('user').order_by('snapshot_time')[:20]
    warned=WarnedUser.objects.select_related('user').order_by('warnes_at')[:2]
    daily = DailyUsage.objects.select_related('user').order_by('-date')[:2]
    monthly = MonthlyUsage.objects.select_related('user').order_by('-year','-month')[:2]
    for d in daily:
        d.total_mb = round(d.total_bytes_used / (1024*1024), 2)

    for m in monthly:
        m.total_mb = round(m.total_bytes_used / (1024*1024), 2)
    return render(request, "hello/report.html",{
        "snapshots":snapshots,
        "daily":daily,
        "monthly":monthly,
        "warned":warned
        })
def edit_usage(request, pk):
    usage = get_object_or_404(DailyUsage, pk=pk)
    form = DailyUsageForm(request.POST or None, instance=usage)
    if form.is_valid():
        form.save()
        return redirect('some-success-url')
    return render(request, 'edit_usage.html', {'form': form})   
    
