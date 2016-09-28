# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
import django_rq
from atmo.clusters.tasks import delete_clusters, update_clusters_info
from atmo.jobs.tasks import launch_jobs
from atmo.workers.tasks import delete_workers


job_schedule = {
    'delete_clusters': {
        'cron_string': '* * * * *',
        'func': delete_clusters,
        'timeout': 5
    },
    'update_clusters_info': {
        'cron_string': '* * * * *',
        'func': update_clusters_info,
        'timeout': 5
    },
    'launch_jobs': {
        'cron_string': '* * * * *',
        'func': launch_jobs,
        'timeout': 5
    },
    'delete_workers': {
        'cron_string': '* * * * *',
        'func': delete_workers,
        'timeout': 5
    },
}


def register_job_schedule():
    scheduler = django_rq.get_scheduler()
    for job_id, params in job_schedule.items():
        scheduler.cron(params['cron_string'], id=job_id,
                       func=params['func'], timeout=params.get('timeout'))
    for job in scheduler.get_jobs():
        if job.id not in job_schedule:
            scheduler.cancel(job)
