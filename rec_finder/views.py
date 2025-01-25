from django.utils import timezone
from django.views import generic, View

from .etl_pipelines.exceptions import UnexpectedDataFormatException
from .models import Venue, Event
from rec_finder.etl_pipelines.city_of_toronto import refresh_data


class StartupDataLoad(View):
    """Run startup script."""
    try:
        refresh_data()
    except UnexpectedDataFormatException as err:
        print(err)


class VenuesView(generic.ListView):
    """Display a complete list of stored venues."""
    model = Venue
    template_name = 'rec_finder/venues_list.html'
    paginate_by = 40


class UpcomingEventsView(generic.ListView):
    """Display upcoming events."""
    template_name = 'rec_finder/upcoming_events_list.html'
    paginate_by = 40

    def get_queryset(self):
        """Return the next 10 upcoming events."""
        return Event.objects.filter(start_time__gte=timezone.now()).order_by(
            "start_time"
        )