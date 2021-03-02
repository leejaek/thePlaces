from django.urls import path

from .views import PlaceCreateView, PlaceView

urlpatterns = [
    path('/', PlaceCreateView.as_view()),
    path('/<int:place_pk>', PlaceView.as_view())
]

