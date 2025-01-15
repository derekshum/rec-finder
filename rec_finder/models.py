from django.db import models
from django.utils import timezone

import dateutil.parser


class Venue(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Event(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        try:
            return f'{dateutil.parser.parse(str(self.start_time)).strftime("%Y-%m-%d %H:%M")} {self.name} at {self.venue.name}'  # i.e. 2025-01-15 13:00 Shinny at Mohawk 4 Ice Centre
        except :
            return f'{self.name} at {self.venue.name}'


    def upcoming_event(self) -> bool:
        return timezone.now() < self.start_time

    def ongoing_event(self) -> bool:
        return self.start_time < timezone.now() < self.end_time
