import requests
import time

from django.conf import settings

from pytwitter import Api

from stacksbots.celery import app

from bots.models import StacksInfo
from bots.utils import hex_to_text

STACKS_BASE_URL = settings.STACKS_BASE_URL
EXPLORER_BASE_URL = settings.EXPLORER_BASE_URL
BNS_CONTRACT_ADDR = 'SP000000000000000000002Q6VF78.bns'

twitter_api = Api(
    consumer_key=settings.CONSUMER_KEY, consumer_secret=settings.CONSUMER_SECRET,
    access_token=settings.ACCESS_TOKEN, access_secret=settings.ACCESS_SECRET
)


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
                    twitter_api.create_tweet(text=tweet_text)

                except Exception as e:
                    raise self.retry(exc=e, countdown=45)

                # To prevent breach of Twitter API rate limit - 200 tweets / 15 mins
                # and also to avoid hitting rate limits for Stacks API
                # (15 x 60) secs / 200 tweets = 4.5 secs per tweet rounded off to 5 secs
                # More here: https://developer.twitter.com/en/docs/twitter-api/rate-limits
                time.sleep(5)

            stacks_info_model.bns_sync_height = block_number
            stacks_info_model.save()
