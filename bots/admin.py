from django.contrib import admin
from django.contrib.auth.models import Group

from bots.models import StacksInfo, BTCName, Leaderboard, Mentions

class StacksInfoAdmin(admin.ModelAdmin):
    list_display = ('bns_sync_height',)
    list_filter = ('bns_sync_height',)

class BTCNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tweeted_at')
    list_filter = ('id', 'name', 'tweeted_at')

class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('id', 'twitter_id', 'twitter_name', 'twitter_username', 'twitter_follower_count', 'is_updated')
    list_filter = ('is_updated',)

class MentionsAdmin(admin.ModelAdmin):
    list_display = ('updated_at',)
    list_filter = ('updated_at',)


admin.site.register(StacksInfo, StacksInfoAdmin)
admin.site.register(BTCName, BTCNameAdmin)
admin.site.register(Leaderboard, LeaderboardAdmin)
admin.site.register(Mentions, MentionsAdmin)
admin.site.unregister(Group)
