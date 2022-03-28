import requests
import time
import tweepy

from datetime import datetime, tzinfo

from django.conf import settings
from django.db.models import Q

from pytwitter import Api

from stacksbots.celery import app

from bots.models import StacksInfo, Leaderboard, Mentions
from bots.utils import hex_to_text

STACKS_BASE_URL = settings.STACKS_BASE_URL
EXPLORER_BASE_URL = settings.EXPLORER_BASE_URL
BNS_CONTRACT_ADDR = 'SP000000000000000000002Q6VF78.bns'
BTC_USER_ID = "1507573158773239811"


# BNS Bot
# Twitter API v2
bns_api_v2 = Api(
    consumer_key=settings.BNS_CONSUMER_KEY, consumer_secret=settings.BNS_CONSUMER_SECRET,
    access_token=settings.BNS_ACCESS_TOKEN, access_secret=settings.BNS_ACCESS_SECRET
)

# BTC Bot
# Twitter API v1
btc_auth_v1 = tweepy.OAuth1UserHandler(
    settings.BTC_CONSUMER_KEY, settings.BTC_CONSUMER_SECRET,
    settings.BTC_ACCESS_TOKEN, settings.BTC_ACCESS_SECRET
)
btc_api_v1 = tweepy.API(btc_auth_v1)

# BTC Bot
# Twitter API v2
btc_api_v2 = Api(
    consumer_key=settings.BTC_CONSUMER_KEY, consumer_secret=settings.BTC_CONSUMER_SECRET,
    access_token=settings.BTC_ACCESS_TOKEN, access_secret=settings.BTC_ACCESS_SECRET
)


def batch_qs(qs, batch_size):
    total = qs.count()
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        yield (start, end, total, qs[start:end])


@app.task(bind=True)
def bns_bot(self):

    stacks_info_model = StacksInfo.objects.get(pk=1)
    first_block = stacks_info_model.bns_sync_height + 1

    try:
        url = f'{STACKS_BASE_URL}/v2/info'
        stacks_info_resp = requests.get(url)
        stacks_info_resp.raise_for_status()

    except requests.exceptions.RequestException as e:
        raise self.retry(exc=e, countdown=45)

    last_block = dict(stacks_info_resp.json())['stacks_tip_height']

    for block_number in range(first_block, last_block + 1):

        try:
            url = f'{STACKS_BASE_URL}/extended/v1/tx/block_height/{block_number}?limit=200'
            stacks_block_resp = requests.get(url)
            stacks_block_resp.raise_for_status()

        except requests.exceptions.RequestException as e:
            raise self.retry(exc=e, countdown=45)

        block = dict(stacks_block_resp.json())
        tx_count = len(block['results'])

        for tx_index in reversed(range(tx_count)):

            tx = block['results'][tx_index]
            should_tweet = False

            if tx['tx_status'] == 'success' and tx['tx_type'] == 'contract_call' and \
                    tx['contract_call']['contract_id'] == BNS_CONTRACT_ADDR:

                if tx['contract_call']['function_name'] == 'name-register':

                    namespace = hex_to_text(
                        tx['contract_call']['function_args'][0]['repr'])
                    name = hex_to_text(
                        tx['contract_call']['function_args'][1]['repr'])
                    text = f'{name}.{namespace} has been registered'
                    tx_id = tx['tx_id']
                    link = f'{EXPLORER_BASE_URL}/txid/{tx_id}?chain=mainnet'
                    should_tweet = True

                elif tx['contract_call']['function_name'] == 'name-transfer':

                    namespace = hex_to_text(
                        tx['contract_call']['function_args'][0]['repr'])
                    name = hex_to_text(
                        tx['contract_call']['function_args'][1]['repr'])
                    from_addr = tx['sender_address']
                    to_addr = tx['contract_call']['function_args'][2]['repr']
                    text = f'{name}.{namespace} has been transferred by {from_addr} to {to_addr}'
                    tx_id = tx['tx_id']
                    link = f'{EXPLORER_BASE_URL}/txid/{tx_id}?chain=mainnet'
                    should_tweet = True

            if should_tweet:

                try:
                    tweet_text = ' '.join([text, link])
                    bns_api_v2.create_tweet(text=tweet_text)

                except Exception as e:
                    raise self.retry(exc=e, countdown=45)

                # To prevent breach of Twitter API rate limit - 200 tweets / 15 mins
                # and also to avoid hitting rate limits for Stacks API
                # (15 x 60) secs / 200 tweets = 4.5 secs per tweet rounded off to 5 secs
                # More here: https://developer.twitter.com/en/docs/twitter-api/rate-limits
                time.sleep(5)

            stacks_info_model.bns_sync_height = block_number
            stacks_info_model.save()


@app.task(bind=True)
def btc_names(self):

    # Max results per page = 20
    # Only first 1000 matching results are returned
    # 1000 / 20 = 50 is the max number of pages
    # More here:
    # https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-search#get-userssearch
    for page_no in range(1, 51):

        try:
            btc_users = btc_api_v1.search_users(
                q="%2Ebtc",
                page=page_no,
                count=20,
                include_entities=False,
            )

        except Exception as e:
            raise self.retry(exc=e, countdown=45)

        for user in btc_users:

            profile_exists = Leaderboard.objects.filter(
                twitter_id=user.id_str).exists()

            if not profile_exists and ".btc" in user.name:

                Leaderboard.objects.create(
                    twitter_id=user.id_str,
                    twitter_name=user.name,
                    twitter_username=user.screen_name,
                    twitter_follower_acount=user.followers_count,
                    is_updated=True,
                )

        # To prevent breach of Twitter API rate limit - 900 requests / 15 mins
        # (15 x 60) secs / 900 requests = 1 sec per request
        # More here:
        # https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-search#resource-information
        time.sleep(1)


@app.task(bind=True)
def leaderboard_update(self):

    leaderboard_objs = Leaderboard.objects.filter(~Q(twitter_id=None))
    batch_size = 100

    for _, _, _, rows in batch_qs(leaderboard_objs, batch_size):

        twitter_ids = []

        for row in rows:
            twitter_ids.append(row.twitter_id)

        try:
            users = btc_api_v1.lookup_users(
                user_id=twitter_ids, include_entities=False)

        except Exception as e:
            raise self.retry(exc=e, countdown=45)

        for i in range(len(users)):

            leaderboard_rows = Leaderboard.objects.filter(
                twitter_id=users[i].id_str)

            if leaderboard_rows.exists() and leaderboard_rows.count() == 1:

                leaderboard_row = leaderboard_rows.first()

                if ".btc" in users[i].name:

                    leaderboard_row.twitter_id = users[i].id_str
                    leaderboard_row.twitter_name = users[i].name
                    leaderboard_row.twitter_username = users[i].screen_name
                    leaderboard_row.twitter_follower_acount = users[i].followers_count
                    leaderboard_row.is_updated = True
                    leaderboard_row.save()

                else:

                    leaderboard_row.delete()

        # To prevent breach of Twitter API rate limit - 900 requests / 15 mins
        # (15 x 60) secs / 900 requests = 1 sec per request
        # More here:
        # https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup#resource-information
        time.sleep(1)

    not_updated_objs = Leaderboard.objects.filter(twitter_id=None)
    batch_size = 100

    for _, _, _, rows in batch_qs(not_updated_objs, batch_size):

        screen_names = []

        for row in rows:
            screen_names.append(row.twitter_username)

        try:
            users = btc_api_v1.lookup_users(
                screen_name=screen_names, include_entities=False)

        except Exception as e:
            raise self.retry(exc=e, countdown=45)

        for i in range(len(users)):

            leaderboard_rows = Leaderboard.objects.filter(
                twitter_username=users[i].screen_name)

            if leaderboard_rows.exists() and leaderboard_rows.count() == 1:

                leaderboard_row = leaderboard_rows.first()
                leaderboard_row.twitter_id = users[i].id_str
                leaderboard_row.twitter_name = users[i].name
                leaderboard_row.twitter_username = users[i].screen_name
                leaderboard_row.twitter_follower_acount = users[i].followers_count
                leaderboard_row.is_updated = True
                leaderboard_row.save()

        # To prevent breach of Twitter API rate limit - 900 requests / 15 mins
        # (15 x 60) secs / 900 requests = 1 sec per request
        # More here:
        # https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup#resource-information
        time.sleep(1)


@app.task(bind=True)
def mentions(self):

    mention_obj = Mentions.objects.get(pk=1)
    start_time = mention_obj.updated_at.replace(tzinfo=None).isoformat(timespec="seconds") + 'Z'
    end_time = datetime.utcnow().replace(tzinfo=None).isoformat(timespec="seconds") + 'Z'
    pagination_token = None

    while True:

        try:
            res = btc_api_v2.get_mentions(
                user_id=BTC_USER_ID,
                start_time=start_time,
                end_time=end_time,
                pagination_token=pagination_token,
                expansions=["author_id"],
                user_fields=["name"],
            )

        except Exception as e:
            raise self.retry(exc=e, countdown=45)

        if res and res.includes and res.includes.users:

            for user in res.includes.users:

                if (".btc" in user.name) and \
                        not Leaderboard.objects.filter(twitter_id=user.id).exists():

                    Leaderboard.objects.create(twitter_id=user.id, is_updated=False)

        if not (res and res.meta and res.meta.next_token):
            break

        pagination_token = res.meta.next_token

        time.sleep(1)

    mention_obj.updated_at = end_time
    mention_obj.save()
