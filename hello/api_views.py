from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated 
from .models import MikrotikUser
from .serializers import MikrotikUserSerializer, DailyUsageSerializer, MonthlyUsageSerializer 
from rest_framework.views import APIView
from rest_framework.response import Response
from hello.models import MikrotikUser, DailyUsage, MonthlyUsage 


class MikrotikUserViewSet(viewsets.ModelViewSet):
    queryset = MikrotikUser.objects.all().order_by('username')
    serializer_class = MikrotikUserSerializer
    permission_classes = [AllowAny]

# ادمین یا هرکس بتواند با username یک کاربر را پیدا کند
class FetchUserAPIView(APIView):
    def get(self, request):
        username = request.query_params.get("username")

        if not username:
            return Response(
                {"error": "username query param is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = MikrotikUser.objects.get(username=username)
        except MikrotikUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        return Response(MikrotikUserSerializer(user).data)
        


# -----------------------------------
# 2) MeDailyUsageAPIView (JWT required)
# -----------------------------------
# مصرف روزانه کاربر لاگین کرده
class MeDailyUsageAPIView(APIView):
    permission_classes = [IsAuthenticated]  # فقط کاربرانی که لاگین هستند

    def get(self, request, format=None):
        # MikrotikUser مربوط به کاربر فعلی جنگو
        try:
            mikrotik_user = MikrotikUser.objects.get(username=request.user.username)
        except MikrotikUser.DoesNotExist:
            return Response({"error": "No MikrotikUser found for this account"}, status=404)

        # رکوردهای روزانه مربوط به این کاربر
        daily_records = DailyUsage.objects.filter(user=mikrotik_user).order_by("-date")[:30]

        if not daily_records.exists():
            return Response({"message": "No daily usage data found"}, status=200)

        serializer = DailyUsageSerializer(daily_records, many=True)
        return Response(serializer.data)

# -------------------------------------
# 3) MeMonthlyUsageAPIView (JWT required)
# -------------------------------------
# مصرف ماهانه کاربر لاگین کرده
class MeMonthlyUsageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            mikrotik_user = MikrotikUser.objects.get(username=request.user.username)
        except MikrotikUser.DoesNotExist:
            return Response({"error": "No MikrotikUser found for this account"}, status=404)

        monthly = MonthlyUsage.objects.filter(
            user=mikrotik_user
        ).order_by("-year", "-month")[:12]

        if not monthly.exists():
            return Response({"message": "No monthly usage data found"}, status=200)

        serializer = MonthlyUsageSerializer(monthly, many=True)
        return Response(serializer.data)
    


# ------------------------------------------------
# 4) MeFetchUsageAPIView (daily + monthly together)
# ------------------------------------------------
# یکجا مصرف روزانه و ماهانه را برمی‌گرداند
class MeFetchUsageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        daily = DailyUsage.objects.filter(user=user).order_by("-date")[:30]
        monthly = MonthlyUsage.objects.filter(user=user).order_by("-month")[:12]

        daily_s = DailyUsageSerializer(daily, many=True)
        monthly_s = MonthlyUsageSerializer(monthly, many=True)

        return Response({
            "daily_usage": daily_s.data,
            "monthly_usage": monthly_s.data
        })    