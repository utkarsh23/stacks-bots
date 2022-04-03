from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, ListView

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

        queryset = Leaderboard.objects.filter(is_updated=True).order_by(
            '-twitter_follower_count')[offset:offset+limit]

        return HttpResponse(leaderboard_api_serializer.serialize(queryset), content_type='application/json')


@method_decorator(csrf_exempt, name='dispatch')
class LeaderboardFrontend(ListView):

    paginate_by = 100
    template_name = 'leaderboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('query')
        if not search_query:
            search_query = ''
        leaderboard = Leaderboard.objects.filter(is_updated=True)
        top_10_floor_objs = leaderboard.order_by('-twitter_follower_count')[:10]
        if top_10_floor_objs.count() != 10:
            top_10_floor = 0
        else:
            top_10_floor = top_10_floor_objs[top_10_floor_objs.count(
            ) - 1].twitter_follower_count
        top_100_floor_objs = leaderboard.order_by('-twitter_follower_count')[:100]
        if top_100_floor_objs.count() != 100:
            top_100_floor = 0
        else:
            top_100_floor = top_100_floor_objs[top_100_floor_objs.count(
            ) - 1].twitter_follower_count
        context['search_query'] = search_query
        context['top_10_rank_floor'] = top_10_floor
        context['top_100_rank_floor'] = top_100_floor
        return context

    def get_queryset(self):
        search_query = self.request.GET.get('query')
        if not search_query:
            search_query = ''
        queryset = Leaderboard.objects.filter(
            Q(is_updated=True) & (
                Q(twitter_name__icontains=search_query) | Q(twitter_username__icontains=search_query))
        ).order_by('-twitter_follower_count')
        return queryset
