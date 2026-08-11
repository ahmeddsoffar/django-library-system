from django.conf import settings
from django.db import migrations


def create_missing_profiles(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    MemberProfile = apps.get_model("Accounts", "MemberProfile")

    existing = set(MemberProfile.objects.values_list("user_id", flat=True))
    MemberProfile.objects.bulk_create([
        MemberProfile(user_id=user_id)
        for user_id in User.objects.values_list("id", flat=True)
        if user_id not in existing
    ])


def noop(apps, schema_editor):
    ## nothing to undo, deleting profiles would destroy real data
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("Accounts", "0004_alter_memberprofile_user"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(create_missing_profiles, noop),
    ]
