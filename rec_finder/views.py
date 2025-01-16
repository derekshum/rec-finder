from django.utils import timezone
from django.views import generic

from .models import Venue, Event


class VenuesView(generic.ListView):
    """Display a complete list of stored venues."""
    model = Venue
    template_name = 'rec_finder/venues_list.html'


class UpcomingEventsView(generic.ListView):
    """Display upcoming events."""
    template_name = 'rec_finder/upcoming_events_list.html'
    context_object_name = "upcoming_events"

    def get_queryset(self):
        """Return the next 10 upcoming events."""
        return Event.objects.filter(start_time__gte=timezone.now()).order_by("start_time")[:10]