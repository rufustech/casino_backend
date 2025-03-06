from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PitViewSet, TableViewSet, PlayerViewSet, HourlyRundownViewSet

# 🔹 Create a Router for ViewSets
router = DefaultRouter()
router.register(r'pits', PitViewSet, basename='pit')
router.register(r'tables', TableViewSet, basename='table')
router.register(r'players', PlayerViewSet, basename='player')
router.register(r'rundowns', HourlyRundownViewSet, basename='rundown')

urlpatterns = [
    path('', include(router.urls)),  # Auto-generates endpoints
]

