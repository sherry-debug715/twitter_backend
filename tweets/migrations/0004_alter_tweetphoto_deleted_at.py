# Generated by Django 5.1.4 on 2025-03-11 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tweets", "0003_tweetphoto"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tweetphoto",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
