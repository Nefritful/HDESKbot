import schedule
import vars
import time
import win32com.client
import logging
from datetime import datetime
from os import environ


def run_job(url, start_time, end_time):
    logging.info('Start job: %s', url)
    if start_time:
        t_now = datetime.now()
        t_start = datetime.strptime(start_time, '%H:%M')
        t_start = t_now.replace(hour=t_start.hour, minute=t_start.minute)
    else:
        t_start = datetime.min
    if end_time:
        t_end = datetime.strptime(end_time, '%H:%M')
        t_end = t_now.replace(hour=t_end.hour, minute=t_end.minute)
    else:
        t_end = datetime.max
    if (t_now >= t_start) and (t_now <= t_end):
        try:
            helpdesk.open("GET", url, False)
            helpdesk.send()
            logging.debug(helpdesk.responseText)
        except Exception as e:
            logging.error("ERROR: %s", e)
        finally:
            logging.info('Finish job: %s', url)


helpdesk = win32com.client.Dispatch('MSXML2.ServerXMLHTTP')

log_path = '{}\\Telebot\\Logs\\cron.log'.format(environ['PROGRAMDATA'])
logging.basicConfig(
        filename=log_path, format='%(asctime)s:%(process)d:%(levelname)s:%(message)s',
        level=vars.log_level)

fixed_time_jobs = [job for job in vars.crontab if job['interval'] == 0]
for job in fixed_time_jobs:
    logging.info('Found job: Run daily at %s, URL: %s', job['start_time'],
                 'http://{}/{}'.format(vars.server, job['url']))

interval_jobs = [job for job in vars.crontab if job['interval'] > 0]
for job in interval_jobs:
    logging.info('Found job: Run every %s minutes, URL: %s, From: %s, Till: %s', job['interval'],
                 'http://{}/{}'.format(vars.server, job['url']),
                 job['start_time'],
                 job['end_time']
                 )


for job in fixed_time_jobs:
    schedule.every().day.at(job['start_time']).do(
        run_job,
        url='http://{}/{}'.format(vars.server, job['url']),
        start_time=job['start_time'],
        end_time=job['end_time'])

for job in interval_jobs:
    schedule.every(job['interval']).minutes.do(
        run_job,
        url='http://{}/{}'.format(vars.server, job['url']),
        start_time=job['start_time'],
        end_time=job['end_time'])

while True:
    schedule.run_pending()
    time.sleep(1)
