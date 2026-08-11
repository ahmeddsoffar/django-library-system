from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MemberProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_member_profile(sender, instance, created, **kwargs):
    ## every user needs a profile, no matter how he was created
    ## (api register, createsuperuser, admin panel)
    if created:
        MemberProfile.objects.get_or_create(user=instance)
