from django.db import models
from django.contrib.auth.models import User

class VolunteerEntry(models.Model):
    CATEGORY_CHOICES = [
        ('sawyer', 'Sawyer'),
        ('trail', 'Trail'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.hours}h)"
