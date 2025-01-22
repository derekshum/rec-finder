from django.utils import timezone
from django.views import generic

from .models import Venue, Event
from .templates.etl_pipelines.city_of_toronto import refresh_data


class VenuesView(generic.ListView):
    """Display a complete list of stored venues."""
    refresh_data()  # TODO keep here?

    model = Venue
    template_name = 'rec_finder/venues_list.html'


class UpcomingEventsView(generic.ListView):
    """Display upcoming events."""
    template_name = 'rec_finder/upcoming_events_list.html'

    def get_queryset(self):
        """Return the next 10 upcoming events."""
        return Event.objects.filter(start_time__gte=timezone.now()).order_by("start_time")[:10]