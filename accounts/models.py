from django.db import models
from django.db import models
from django.utils import timezone
import datetime
import random
from django.conf import settings

class PasswordResetPIN(models.Model):
    email = models.EmailField()
    pin = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Check if the PIN is less than 10 minutes old
        return self.created_at > timezone.now() - datetime.timedelta(minutes=settings.PASSWORD_PIN_TIMEOUT_MINUTES)