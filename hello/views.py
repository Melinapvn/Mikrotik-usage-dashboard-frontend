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
from .serializers import DailyUsageSerializer,MonthlyUsageSerializer,CustomerSerializer
from datetime import date
from rest_framework.decorators import api_view
import csv, io
from reportlab.pdfgen import canvas
from openpyxl import Workbook


 
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

@api_view(['GET'])
def monthly_calculate_api(request):
    data = MonthlyUsage.objects.all().order_by('year','-month')
    serializer = MonthlyUsageSerializer(data, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def export_daily_usage_pdf(request):
    data = DailyUsage.objects.all()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="daily_usage.pdf"'
    p = canvas.Canvas(response)
    y = 800
    p.drawString(200, y, "Daily Usage Report")
    y -= 40
    for obj in data:
        text = f"User: {obj.user}, Total: {obj.total_bytes_used}, Date: {obj.date}"
        p.drawString(50, y, text)
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
    p.showPage()
    p.save()
    return response


@api_view(['GET'])
def export_daily_usage_csv(request):
    data = DailyUsage.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="daily_usage.csv"'
    writer = csv.writer(response)
    writer.writerow(['User', 'Total Bytes Used', 'Date'])
    for obj in data:
        writer.writerow([obj.user, obj.total_bytes_used, obj.date])
    return response


@api_view(['GET'])
def export_daily_usage_excel(request):
    data = DailyUsage.objects.select_related('user').all()
    wb = Workbook()
    ws = wb.active
    ws.title = "Daily Usage"
    ws.append(['User', 'Total Bytes Used', 'Date'])

    for obj in data:
        # اگر مدل MikrotikUser مثلاً فیلد username یا name دارد:
        username = getattr(obj.user, 'username', str(obj.user))
        ws.append([username, obj.total_bytes_used, str(obj.date)])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="daily_usage.xlsx"'
    wb.save(response)
    return response
    
@api_view(['GET'])
def top_consumers_daily(request):
    today = date.today()

    data = (
        DailyUsage.objects.filter(date=today)
        .values('user__username', 'total_bytes_used')
        .order_by('-total_bytes_used')[:5]
    )

    return Response(list(data))    




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
    

