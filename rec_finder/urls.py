from django.urls import path

from . import views

app_name = "finder"
urlpatterns = [
    path("venues", views.VenuesView.as_view(), name="venues"),
    path("upcoming-events", views.UpcomingEventsView.as_view(), name="upcoming_events"),
]