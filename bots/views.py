from django.core import serializers
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic.base import View

from bots.models import Leaderboard
from bots.serializers import leaderboard_api_serializer

class LeaderboardApi(View):

    def get(self, request, *args, **kwargs):

        # Max limit = 200
        # Default limit = 50
        limit_str = request.GET.get('limit')

        if not (limit_str and limit_str.isnumeric()):
            limit = 50
        else:
            limit = int(limit_str)

        if limit > 200:
            return HttpResponseBadRequest('Max limit can be 200', content_type='application/json')

        offset_str = request.GET.get('offset')
        if not (offset_str and offset_str.isnumeric()):
            offset = 0
        else:
            offset = int(offset_str)

        queryset = Leaderboard.objects.filter(is_updated=True).order_by('-twitter_follower_count')[offset:offset+limit]

        return HttpResponse(leaderboard_api_serializer.serialize(queryset), content_type='application/json')
