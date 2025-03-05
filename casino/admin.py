from django.contrib import admin
from .models import CustomUser, Pit, Table, Player, HourlyRundown
from django.contrib.auth.models import User



# Register your models here.
# casino/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Pit, Table, Player, HourlyRundown


# 🔹 Registering the Custom User Model with Admin


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

admin.site.register(CustomUser, CustomUserAdmin)


# 🔹 Registering PIT Model with Admin
class PitAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by')
    search_fields = ('name',)
    list_filter = ('created_by',)

admin.site.register(Pit, PitAdmin)

# 🔹 Registering Table Model with Admin
class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'game_type', 'pit', 'created_by')
    search_fields = ('name', 'game_type')
    list_filter = ('game_type', 'pit', 'created_by')

admin.site.register(Table, TableAdmin)

# 🔹 Registering Player Model with Admin
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'table', 'buy_in', 'cash_out', 'average_bet', 'session_start', 'session_end', 'reward_points')
    search_fields = ('name',)
    list_filter = ('table',)

admin.site.register(Player, PlayerAdmin)

# 🔹 Registering HourlyRundown Model with Admin
class HourlyRundownAdmin(admin.ModelAdmin):
    list_display = ('table', 'timestamp', 'float_amount', 'drop_amount', 'profit_loss', 'entered_by')
    search_fields = ('table__name',)
    list_filter = ('table', 'entered_by')

admin.site.register(HourlyRundown, HourlyRundownAdmin)
