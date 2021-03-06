# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from .utils import calculate_fingerprint
from ..models import CreatedByModel, EditedAtModel


@python_2_unicode_compatible
class SSHKey(CreatedByModel, EditedAtModel):
    VALID_PREFIXES = [
        'ssh-rsa',
        'ssh-dss',
        'ecdsa-sha2-nistp256',
        'ecdsa-sha2-nistp384',
        'ecdsa-sha2-nistp521',
    ]

    title = models.CharField(
        max_length=100,
        help_text='Name to give to this public key',
    )
    key = models.TextField(
        help_text='Should start with one of the following prefixes: %s' %
                  ', '.join(VALID_PREFIXES),
    )
    fingerprint = models.CharField(
        max_length=48,
        blank=True,
    )

    class Meta:
        permissions = [
            ('view_sshkey', 'Can view SSH key'),
        ]
        unique_together = (
            ('created_by', 'fingerprint')
        )

    def __str__(self):
        return self.title

    def __repr__(self):
        return "<SSHKey {} ({})>".format(self.title, self.fingerprint)

    def get_absolute_url(self):
        return reverse('keys-detail', kwargs={'id': self.id})

    @property
    def prefix(self):
        return self.key.strip().split()[0]

    def save(self, *args, **kwargs):
        if not self.fingerprint and self.key:
            self.fingerprint = calculate_fingerprint(self.key)
        super(SSHKey, self).save(*args, **kwargs)
