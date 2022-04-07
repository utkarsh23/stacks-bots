from django_celery_beat.models import CrontabSchedule, PeriodicTask


bns_bot_schedule, _ = CrontabSchedule.objects.get_or_create(
    minute='0',
    hour='*',
    day_of_month='*',
    month_of_year='*',
    day_of_week='*',
)
PeriodicTask.objects.create(
    crontab=bns_bot_schedule,
    name='BNS Bot',
    task='bots.tasks.bns_bot',
)

btc_weekly_update_schedule, _ = CrontabSchedule.objects.get_or_create(
    minute='10',
    hour='0',
    day_of_month='*',
    month_of_year='*',
    day_of_week='0',
)
PeriodicTask.objects.create(
    crontab=btc_weekly_update_schedule,
    name='BTC Weekly Update',
    task='bots.tasks.btc_weekly_update',
)

btc_names_schedule, _ = CrontabSchedule.objects.get_or_create(
    minute='15',
    hour='*',
    day_of_month='*',
    month_of_year='*',
    day_of_week='*',
)
PeriodicTask.objects.create(
    crontab=btc_names_schedule,
    name='BTC Names',
    task='bots.tasks.btc_names',
)

btc_monthly_review_schedule, _ = CrontabSchedule.objects.get_or_create(
    minute='25',
    hour='0',
    day_of_month='1',
    month_of_year='*',
    day_of_week='*',
)
PeriodicTask.objects.create(
    crontab=btc_monthly_review_schedule,
    name='BTC Monthly Review',
    task='bots.tasks.btc_monthly_review',
)

leaderboard_update_schedule, _ = CrontabSchedule.objects.get_or_create(
    minute='30',
    hour='*',
    day_of_month='*',
    month_of_year='*',
    day_of_week='*',
)
PeriodicTask.objects.create(
    crontab=leaderboard_update_schedule,
    name='Leaderboard Update',
    task='bots.tasks.leaderboard_update',
)

mentions_schedule, _ = CrontabSchedule.objects.get_or_create(
    minute='*/2',
    hour='*',
    day_of_month='*',
    month_of_year='*',
    day_of_week='*',
)
PeriodicTask.objects.create(
    crontab=mentions_schedule,
    name='Mentions',
    task='bots.tasks.mentions',
)
