# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from atmo.clusters.models import Cluster
from atmo.utils import email


class Command(BaseCommand):
    help = 'Go through expired clusters to deactivate or warn about ones that are expiring'

    def handle(self, *args, **options):
        now = timezone.now()
        for cluster in Cluster.objects.exclude(most_recent_status__in=Cluster.FINAL_STATUS_LIST):
            # The cluster is expired
            if cluster.end_date < now:
                cluster.deactivate()
            # The cluster will expire soon
            elif cluster.end_date < now + timedelta(hours=1):
                email.send_email(
                    email_address=cluster.created_by.email,
                    subject="Cluster {} is expiring soon!".format(cluster.identifier),
                    body=(
                        "Your cluster {} will be terminated in roughly one hour, around {}. "
                        "Please save all unsaved work before the machine is shut down.\n"
                        "\n"
                        "This is an automated message from the Telemetry Analysis service. "
                        "See https://analysis.telemetry.mozilla.org/ for more details."
                    ).format(cluster.identifier, now + timedelta(hours=1))
                )
