from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Pit, Table, Player, HourlyRundown
from .serializers import PitSerializer, TableSerializer, PlayerSerializer, HourlyRundownSerializer, UserSerializer  


User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAdminUser])  # Only Admins can create Supervisors
def register_supervisor(request):
    """Registers a new Supervisor user (Only Admins can do this)"""
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")

    if not (username and password and email):
        return Response({"error": "All fields are required"}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    user.role = "supervisor"  # Assign Supervisor role
    user.save()

    return Response({"message": "Supervisor registered successfully", "user": UserSerializer(user).data}, status=201)
# 🔹 Custom Permission Classes
class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'supervisor'

class IsPitBoss(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'pit_boss'

# 🔹 PIT ViewSet (CRUD for Supervisors)
class PitViewSet(viewsets.ModelViewSet):
    queryset = Pit.objects.all()
    serializer_class = PitSerializer
    permission_classes = [IsSupervisor]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# 🔹 Table ViewSet (CRUD for Supervisors)
class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = [IsSupervisor]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# 🔹 Player ViewSet (CRUD for PIT Bosses)
class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsPitBoss]

    def perform_create(self, serializer):
        serializer.save(entered_by=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        """Handle Buy-in & Cash-out Updates"""
        player = get_object_or_404(Player, pk=kwargs['pk'])
        buy_in = request.data.get("buy_in")
        cash_out = request.data.get("cash_out")

        if buy_in is not None:
            player.buy_in += float(buy_in)
        if cash_out is not None:
            player.cash_out = float(cash_out)

        player.save()
        return Response(PlayerSerializer(player).data)

# 🔹 Hourly Rundown ViewSet (CRUD for PIT Bosses)
class HourlyRundownViewSet(viewsets.ModelViewSet):
    queryset = HourlyRundown.objects.all().order_by('-timestamp')
    serializer_class = HourlyRundownSerializer
    permission_classes = [IsPitBoss]

    def perform_create(self, serializer):
        rundown = serializer.save(entered_by=self.request.user)
        rundown.calculate_profit_loss()
        return Response(HourlyRundownSerializer(rundown).data)
