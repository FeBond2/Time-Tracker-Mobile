# Data migration: add default categories (Work, Personal, Household, Leisure, Social) for all users

from django.db import migrations

DEFAULT_NAMES = ["Work", "Personal", "Household", "Leisure", "Social"]


def add_default_categories(apps, schema_editor):
    User = apps.get_model("core", "User")
    EntryCategory = apps.get_model("core", "EntryCategory")
    for user in User.objects.all():
        for name in DEFAULT_NAMES:
            EntryCategory.objects.get_or_create(user=user, name=name)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_add_time_entry_order"),
    ]

    operations = [
        migrations.RunPython(add_default_categories, noop),
    ]
