from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_donor = models.BooleanField(default=False)
    is_requester = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        roles = []
        if self.is_donor:
            roles.append('donor')
        if self.is_requester:
            roles.append('requester')
        if self.is_admin:
            roles.append('admin')
        return f"{self.user.username} ({', '.join(roles) or 'no role'})"