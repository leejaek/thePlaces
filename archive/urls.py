from django.urls import path

from .views import CheckInView, CheckInDeleteView #, ReviewView

urlpatterns = [
    path('/checkin/place/<int:place_pk>', CheckInView.as_view()),
    path('/checkin/<int:checkin_pk>', CheckInDeleteView.as_view())
#    path('/review/place/<int:place_pk>', ReviewView.as_view())
]

