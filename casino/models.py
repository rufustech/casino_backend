from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import User
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):  # Inherit from AbstractUser instead of models.Model
    ROLE_CHOICES = [
        ('supervisor', 'Supervisor'),
        ('pit_boss', 'Pit Boss'),
        # Add any other roles here
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, blank=True, null=True)

    objects = CustomUserManager()  # Set the custom manager

    def __str__(self):
        return f"{self.username} ({self.role})"


# 🔹 PIT (Created by Supervisors)
class Pit(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="created_pits")
    

    def __str__(self):
        return self.name

# 🔹 Table (Created by Supervisors, Managed by PIT Bosses)
class Table(models.Model):
    GAME_CHOICES = [
        ('Blackjack', 'Blackjack'),
        ('Craps', 'Craps'),
        ('Roulette', 'Roulette'),
        ('Poker', 'Poker'),
        ('Baccarat', 'Baccarat'),
    ]
    name = models.CharField(max_length=50)
    pit = models.ForeignKey(Pit, on_delete=models.CASCADE, related_name="tables")
    game_type = models.CharField(max_length=50, choices=GAME_CHOICES)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="created_tables")


    def __str__(self):
        return f"{self.name} ({self.game_type})"

# 🔹 Player (Tracked by PIT Bosses)
class Player(models.Model):
    name = models.CharField(max_length=100)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, related_name="players")
    buy_in = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cash_out = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    average_bet = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    session_start = models.DateTimeField(null=True, blank=True)
    session_end = models.DateTimeField(null=True, blank=True)
    reward_points = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    entered_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="entered_players")

    def __str__(self):
        return f"{self.name} at {self.table.name if self.table else 'No Table'}"


    def calculate_play_time(self):
        """Calculate session duration in minutes."""
        if self.session_start and self.session_end:
            return (self.session_end - self.session_start).total_seconds() // 60
        return 0

# 🔹 Hourly Rundown (Logged by PIT Bosses)
class HourlyRundown(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="rundowns")
    timestamp = models.DateTimeField(auto_now_add=True)
    float_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    drop_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profit_loss = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    entered_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="entered_rundowns")


    def calculate_profit_loss(self):
        """Calculate profit/loss as Float - Drop"""
        self.profit_loss = self.float_amount - self.drop_amount
        self.save()

    def __str__(self):
        return f"Rundown for {self.table.name} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
