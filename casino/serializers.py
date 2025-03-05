from rest_framework import serializers
from .models import User, Pit, Table, Player, HourlyRundown

# 🔹 User Serializer (Handles Supervisors & PIT Bosses)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

# 🔹 PIT Serializer (Created by Supervisors)
class PitSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)  # Nested User data (Supervisor)

    class Meta:
        model = Pit
        fields = ['id', 'name', 'created_by']

# 🔹 Table Serializer (Includes PIT Data)
class TableSerializer(serializers.ModelSerializer):
    pit = PitSerializer(read_only=True)  # Nested PIT data
    created_by = UserSerializer(read_only=True)  # Supervisor details

    class Meta:
        model = Table
        fields = ['id', 'name', 'game_type', 'pit', 'created_by']

# 🔹 Player Serializer (Includes Play Time Calculation)
class PlayerSerializer(serializers.ModelSerializer):
    table = TableSerializer(read_only=True)  # Nested Table details
    entered_by = UserSerializer(read_only=True)  # PIT Boss details
    play_time = serializers.SerializerMethodField()  # Custom field for session duration

    class Meta:
        model = Player
        fields = [
            'id', 'name', 'table', 'buy_in', 'cash_out', 'bet_amount', 'average_bet',
            'session_start', 'session_end', 'reward_points', 'description', 'entered_by', 'play_time'
        ]

    def get_play_time(self, obj):
        return obj.calculate_play_time()  # Returns session duration in minutes

# 🔹 Hourly Rundown Serializer (Includes Profit/Loss Calculation)
class HourlyRundownSerializer(serializers.ModelSerializer):
    table = TableSerializer(read_only=True)  # Nested Table details
    entered_by = UserSerializer(read_only=True)  # PIT Boss details
    profit_loss = serializers.SerializerMethodField()  # Custom profit/loss calculation

    class Meta:
        model = HourlyRundown
        fields = ['id', 'table', 'timestamp', 'float_amount', 'drop_amount', 'profit_loss', 'entered_by']

    def get_profit_loss(self, obj):
        obj.calculate_profit_loss()  # Updates profit/loss before returning
        return obj.profit_loss  # Returns the updated value
