# Generated by Django 4.1.13 on 2025-02-20 15:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0005_alter_post_publish"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="post",
            options={
                "ordering": ["-publish"],
                "verbose_name_plural": "Markdown Content",
            },
        ),
    ]
