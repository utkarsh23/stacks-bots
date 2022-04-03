from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from bots.views import LeaderboardFrontend, LeaderboardApi

urlpatterns = [
    path('', LeaderboardFrontend.as_view(), name='leaderboard'),
    path('api/', LeaderboardApi.as_view(), name='api'),
] + (static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +
     static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))

app_name = 'bots'
