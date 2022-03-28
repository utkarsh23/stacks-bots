from django.contrib import admin
from django.contrib.auth.models import Group

from bots.models import Leaderboard, Mentions

class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('id', 'twitter_id', 'twitter_name', 'twitter_username', 'twitter_follower_acount', 'is_updated')
    list_filter = ('is_updated',)

class MentionsAdmin(admin.ModelAdmin):
    list_display = ('updated_at',)
    list_filter = ('updated_at',)


admin.site.register(Leaderboard, LeaderboardAdmin)
admin.site.register(Mentions, MentionsAdmin)
admin.site.unregister(Group)
