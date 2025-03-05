from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Pit, Table, Player
from .serializers import PitSerializer, TableSerializer, PlayerSerializer

User = get_user_model()

# 🔹 Create a PIT (Only Supervisors)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_pit(request):
    if request.user.role != 'supervisor':
        return Response({"error": "Permission denied"}, status=403)

    name = request.data.get("name")
    pit = Pit.objects.create(name=name, created_by=request.user)
    return Response(PitSerializer(pit).data)

# 🔹 Create a Table (Only Supervisors)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_table(request):
    if request.user.role != 'supervisor':
        return Response({"error": "Permission denied"}, status=403)

    pit_id = request.data.get("pit_id")
    name = request.data.get("name")
    game_type = request.data.get("game_type")

    try:
        pit = Pit.objects.get(id=pit_id)
        table = Table.objects.create(name=name, game_type=game_type, pit=pit, created_by=request.user)
        return Response(TableSerializer(table).data)
    except Pit.DoesNotExist:
        return Response({"error": "PIT not found"}, status=404)

# 🔹 Add Player (Only PIT Bosses)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_player(request):
    if request.user.role != 'pit_boss':
        return Response({"error": "Permission denied"}, status=403)

    serializer = PlayerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(entered_by=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# 🔹 Update Buy-in & Cash-out (Only PIT Bosses)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_player_funds(request, player_id):
    if request.user.role != 'pit_boss':
        return Response({"error": "Permission denied"}, status=403)

    try:
        player = Player.objects.get(id=player_id)
        buy_in = request.data.get("buy_in")
        cash_out = request.data.get("cash_out")

        if buy_in is not None:
            player.buy_in += float(buy_in)  # Incremental buy-in update
        if cash_out is not None:
            player.cash_out = float(cash_out)

        player.save()
        return Response(PlayerSerializer(player).data)
    except Player.DoesNotExist:
        return Response({"error": "Player not found"}, status=404)
    
    # 🔹 Add Hourly Rundown (Only PIT Bosses)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_hourly_rundown(request):
    if request.user.role != 'pit_boss':
        return Response({"error": "Permission denied"}, status=403)

    table_id = request.data.get("table_id")
    float_amount = request.data.get("float_amount")
    drop_amount = request.data.get("drop_amount")

    try:
        table = Table.objects.get(id=table_id)
        rundown = HourlyRundown.objects.create(
            table=table,
            float_amount=float(float_amount),
            drop_amount=float(drop_amount),
            entered_by=request.user
        )
        rundown.calculate_profit_loss()  # Update Profit/Loss
        return Response({"message": "Hourly Rundown added successfully", "data": {
            "table": table.name,
            "float_amount": rundown.float_amount,
            "drop_amount": rundown.drop_amount,
            "profit_loss": rundown.profit_loss
        }}, status=201)
    except Table.DoesNotExist:
        return Response({"error": "Table not found"}, status=404)

# 🔹 Get Real-Time Rundowns (Supervisors)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rundowns(request):
    if request.user.role != 'supervisor':
        return Response({"error": "Permission denied"}, status=403)

    rundowns = HourlyRundown.objects.all().order_by('-timestamp')  # Latest first
    data = [{
        "table": rundown.table.name,
        "timestamp": rundown.timestamp.strftime('%Y-%m-%d %H:%M'),
        "float_amount": rundown.float_amount,
        "drop_amount": rundown.drop_amount,
        "profit_loss": rundown.profit_loss,
        "entered_by": rundown.entered_by.username
    } for rundown in rundowns]

    return Response({"rundowns": data}, status=200)


# 🔹 Add Hourly Rundown (Only PIT Bosses)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_hourly_rundown(request):
    if request.user.role != 'pit_boss':
        return Response({"error": "Permission denied"}, status=403)

    table_id = request.data.get("table_id")
    float_amount = request.data.get("float_amount")
    drop_amount = request.data.get("drop_amount")

    try:
        table = Table.objects.get(id=table_id)
        rundown = HourlyRundown.objects.create(
            table=table,
            float_amount=float(float_amount),
            drop_amount=float(drop_amount),
            entered_by=request.user
        )
        rundown.calculate_profit_loss()  # Update Profit/Loss
        return Response({"message": "Hourly Rundown added successfully", "data": {
            "table": table.name,
            "float_amount": rundown.float_amount,
            "drop_amount": rundown.drop_amount,
            "profit_loss": rundown.profit_loss
        }}, status=201)
    except Table.DoesNotExist:
        return Response({"error": "Table not found"}, status=404)

# 🔹 Get Real-Time Rundowns (Supervisors)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rundowns(request):
    if request.user.role != 'supervisor':
        return Response({"error": "Permission denied"}, status=403)

    rundowns = HourlyRundown.objects.all().order_by('-timestamp')  # Latest first
    data = [{
        "table": rundown.table.name,
        "timestamp": rundown.timestamp.strftime('%Y-%m-%d %H:%M'),
        "float_amount": rundown.float_amount,
        "drop_amount": rundown.drop_amount,
        "profit_loss": rundown.profit_loss,
        "entered_by": rundown.entered_by.username
    } for rundown in rundowns]

    return Response({"rundowns": data}, status=200)

