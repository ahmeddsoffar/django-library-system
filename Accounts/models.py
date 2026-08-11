from django.db import models
from django.conf import settings

class MemberProfile(models.Model):
    ##cascade if user deleted delete all related data
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='member_profile') 

    ## null for tells db this can be null , and blank telss django validation it can be empty
    ##phone_number = models.CharField(max_length=15, null=True, blank=True) 
    ##address = models.TextField(null=True, blank=True)

    max_books_allowed = models.PositiveIntegerField(default=5)
    active_status = models.BooleanField(default=True)


    def __str__(self): ## rather than returning objects
        return f"{self.user.username} profile"

