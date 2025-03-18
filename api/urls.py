from django.urls import path
from . import views
from .views import get_polls, create_poll, poll_detail, create_choice, choice_detail


urlpatterns = [
    # Polls
    path("polls/", get_polls, name="get_polls"),
    path("polls/create", create_poll, name="create_poll"),
    path("polls/<int:pk>", poll_detail, name="poll_detail"),

    # Choices
    path("choices/create", create_choice, name="create_choice"),
    path("choices/<int:pk>", choice_detail, name="choice_detail"),
]