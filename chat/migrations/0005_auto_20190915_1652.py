# Generated by Django 2.2.4 on 2019-09-15 11:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_auto_20190909_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='to_user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_messages', to=settings.AUTH_USER_MODEL),
        ),
    ]
