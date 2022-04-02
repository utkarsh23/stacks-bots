from django.core.serializers.json import Serializer


class LeaderboardApiSerializer(Serializer):

    def get_dump_object(self, obj):
        data = super().get_dump_object(obj)
        del data['model']
        del data['pk']
        del data['fields']
        data['twitter_id'] = obj.twitter_id
        data['twitter_name'] = obj.twitter_name
        data['twitter_username'] = obj.twitter_username
        data['twitter_follower_count'] = obj.twitter_follower_count
        return data


leaderboard_api_serializer = LeaderboardApiSerializer()
