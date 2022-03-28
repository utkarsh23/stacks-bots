from django.urls import path

from bots.views import LeaderboardApi

urlpatterns = [
    path('api/', LeaderboardApi.as_view(), name='api'),
]

app_name = 'bots'
