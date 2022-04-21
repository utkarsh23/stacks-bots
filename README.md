# Twitter Bots for Stacks: BNS Bot & `.btc` Leaderboard Bot

This project is supported by a generous grant from the [Stacks Foundation](https://stacks.org/).<br />You can read more about the grant here: [https://grants.stacks.org/dashboard/grants/304](https://grants.stacks.org/dashboard/grants/304)

| Bot | Description | Links |
| --- | --- | --- |
| BNS Bot | Tweets events for BNS names that are registered or transferred from one account to another | Twitter: [@bns_bot](https://twitter.com/bns_bot) |
| `.btc` Leaderboard Bot | Tweets major events for all `.btc` names and maintains a `.btc` Leaderboard | Twitter: [@btc_leaderboard](https://twitter.com/btc_leaderboard)<br />Leaderboard: [btcleaderboard.xyz](https://btcleaderboard.xyz/)<br />API Docs: [btcleaderboard.xyz/api-docs/](https://btcleaderboard.xyz/api-docs/) |

## Navigating the project code
* This project is a [Django](https://www.djangoproject.com/) project with Postgres Database.
* [Celery](https://docs.celeryq.dev/en/stable/index.html) & [Celery Beat](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html#using-custom-scheduler-classes) are responsible for running cron jobs. **Celery** runs all jobs and **celery beat** is responsible for periodically creating jobs and pushing them to **celery**.
* The project contains only a single Django app, called **bots** and the `/bots` folder contains all logic for this app.
* All cron jobs logic is written in the file: `/bots/tasks.py`
* `setup_jobs.py` is the script that you need to run initially to create all cron jobs.

In the file `/bots/tasks.py` you will find 6 cron jobs:
| Job | Bot | Description | Frequency |
| --- | --- | --- | --- |
| bns_bot | BNS | Tweets BNS registration and transfer events  | Once every hour |
| btc_weekly_update | BTC | Tweets the number of `.btc` names registered in the past week | Once every week |
| btc_names | BTC | Runs a twitter search query for users with `.btc` in their twitter name and if a new name is found and has entered the top 100 in the leaderboard it also tweets this event | Once every hour |
| btc_monthly_review | BTC | Tweets the number of `.btc` names in the leaderboard, top 10 rank floor and top 100 rank floor | Once every month |
| leaderboard_update | BTC | Runs a twiter lookup on all records in the leaderboard, updates their details like follower count and removes the names that no longer contain the `.btc` name | Once every hour |
| mentions | BTC | Fetches all tweets mentioning `@btc_leaderboard`, checks if the author contains a `.btc` twitter name and if so, adds it to the leaderboard | Once every 2 minutes |
## Navigating the documentation code
* All documentation code can be found in the `/docs` folder.
* The project is a Swagger UI implemented in React.
* `/docs/src/spec.js` contains the JSON spec for Swagger.
