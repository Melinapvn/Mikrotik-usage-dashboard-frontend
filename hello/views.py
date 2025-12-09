from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserUsage,MikrotikUser
from .serializers import UserUsageSerializer
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from hello.models import DailyUsage,MonthlyUsage,UserUsage,MikrotikUser,WarnedUser
# Create your views here.
from django.http import HttpResponse 
from .models import Customer
from rest_framework import viewsets,status
from rest_framework.decorators import api_view,permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Customer
from .serializers import DailyUsageSerializer,MonthlyUsageSerializer,CustomerSerializer,MonthlyUsageSerializer,FetchUserSerializer
from datetime import date
import csv, io
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from rest_framework.permissions import IsAuthenticatedOrReadOnly,AllowAny
from hello.utils.mikrotik_fetch import fetch_mikrotik
from hello.utils.aggregate import calculate_daily_usage, calculate_monthly_usage_for_user
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

user=get_user_model


 
@api_view(['GET']) 
@permission_classes([AllowAny])
@authentication_classes([])
def daily_usage_api(request):

    data = UserUsage.objects.all().order_by('-snapshot_time')
    serializer = UserUsageSerializer(data, many=True)
    return Response(serializer.data) 

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def daily_calculate_api(request):
    today=date.today()
    data = DailyUsage.objects.filter(date=today).order_by('-date')
    serializer = DailyUsageSerializer(data, many=True)
    return Response(serializer.data)  

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def monthly_calculate_api(request):
    today=date.today()
    data = MonthlyUsage.objects.filter(year=today.year,month=today.month).order_by('-total_bytes_used')
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
@permission_classes([AllowAny])
@authentication_classes([])
def top_consumers_daily(request):
    today = date.today()

    data = (
        DailyUsage.objects.filter(date=today)
        .values('user__username', 'total_bytes_used')
        .order_by('-total_bytes_used')[:5]
    )

    return Response(list(data))    
    
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def top_consumers_monthly(request):
    today = date.today()

    data = (
        MonthlyUsage.objects
        .filter(year=today.year, month=today.month)
        .values('user__username', 'total_bytes_used')
        .order_by('-total_bytes_used')[:5]
    )

    return Response(list(data))    

class FetchUserAPIView(APIView):
    permission_classes = (AllowAny,)  # یا IsAdminUser اگر می‌خواهی فقط ادمین بزند
    def post(self, request):
        serializer = FetchUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        try:
            fetch_mikrotik(username=username)   # این تابع قبلاً کار می‌کند
            return Response({"status":"ok", "message": f"usage updated for {username}"})
        except Exception as e:
            return Response({"status":"error","message":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------- API های مخصوص user (require auth) ----------
class MeFetchUsageAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        username = request.user.username
        try:
            fetch_mikrotik(username=username)
            return Response({"status":"ok","message":f"usage updated for {username}"})
        except Exception as e:
            return Response({"status":"error","message":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MeDailyUsageAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user = request.user
        # فرض می‌گیریم calculate_daily_usage_for_user_both وجود داره و عدد برمی‌گرداند
        try:
            # نمونه: تابع باید مقدار روزانه را برگرداند (بایت)
            daily = calculate_daily_usage(user)  # یا تابعی که تو داری
            return Response({"user": user.username, "daily_total": daily})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class MeMonthlyUsageAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        user = request.user
        try:
            monthly = calculate_monthly_usage_for_user(user)
            return Response({"user": user.username, "monthly_total": monthly})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


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
    

