# Generated by Django 3.0.5 on 2020-04-08 12:44

import json
from collections import namedtuple

from django.db import migrations, connection

from allauth.socialaccount.models import SocialAccount


def migrate_social_accounts(_, __):
    if 'social_auth_usersocialauth' in connection.introspection.table_names():
        with connection.cursor() as cursor:
            OldAccount = namedtuple('OldAccount', ('id', 'provider', 'uid', 'extra_data', 'user_id'))
            cursor.execute("SELECT * FROM social_auth_usersocialauth")

            for row in cursor.fetchall():
                row = OldAccount(*row)
                new_account = SocialAccount(provider=row.provider, uid=row.uid, extra_data=json.loads(row.extra_data))
                new_account.user_id = row.user_id
                new_account.save()


def unmigrate_social_accounts(_, __):
    SocialAccount.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0033_auto_20200408_1232'),
        ('socialaccount', '0003_extra_data_default_dict'),
    ]

    operations = [
        migrations.RunPython(migrate_social_accounts, unmigrate_social_accounts),
    ]
