# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-01-16 14:51
from __future__ import unicode_literals

from django.db import migrations

from atmo.models import PermissionMigrator
from ...keys.utils import calculate_fingerprint


def ssh_key_mapping(apps):
    "create a mapping of key fingerprint -> list of clusters"
    Cluster = apps.get_model('clusters', 'Cluster')
    ssh_keys = {}
    for cluster in Cluster.objects.all():
        fingerprint = calculate_fingerprint(cluster.public_key.strip())
        ssh_keys.setdefault(fingerprint, []).append(cluster)
    return ssh_keys


def migrate_public_keys(apps, schema_editor):
    SSHKey = apps.get_model('keys', 'SSHKey')

    # create a mapping of key fingerprint -> list of clusters
    ssh_keys = ssh_key_mapping(apps)

    # go through the mapping and create a title for the key
    for fingerprint, clusters in ssh_keys.items():
        # cut off after 100 characters in case of lots of clusters
        title = 'key used on: ' + ','.join([cluster.identifier for cluster in clusters])
        ssh_key = SSHKey(
            title=title[:100],
            key=clusters[0].public_key.strip(),
            created_by=cluster.created_by,
            fingerprint=fingerprint,
        )
        ssh_key.save()

    PermissionMigrator(apps, SSHKey, 'created_by', 'view').assign()
    PermissionMigrator(apps, SSHKey, 'created_by', 'change').assign()
    PermissionMigrator(apps, SSHKey, 'created_by', 'delete').assign()


def rollback_public_keys(apps, schema_editor):
    SSHKey = apps.get_model('keys', 'SSHKey')
    ssh_keys = ssh_key_mapping(apps)
    SSHKey.objects.filter(fingerprint__in=set(list(ssh_keys.keys()))).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('keys', '0002_assign_view_perms'),
        ('clusters', '0012_cluster_ssh_key'),
    ]

    operations = [
        migrations.RunPython(
            migrate_public_keys,
            rollback_public_keys,
        ),
    ]
