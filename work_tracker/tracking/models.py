# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from accounts.models import Organization


class WorkPeriod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(blank=True, null=True)

    @property
    def duration(self):
        # Aseguramos que la fecha de fin esté después de la de inicio
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds()
        return 0

    def __str__(self):
        return f"{self.user.username} - {self.start_time} to {self.end_time or 'Ongoing'}"
