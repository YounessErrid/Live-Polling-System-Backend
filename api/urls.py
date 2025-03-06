from django.urls import path
from . import views
from .views import profile_view, register_user


urlpatterns = [
    # User management
    path("user/register/", register_user, name="register"),
    path("profile/", profile_view, name="profile"),  # No need for <int:pk>

    # Polls
    path("polls/", views.PollListCreate.as_view(), name="polls_list"),
    path("polls/<int:pk>/", views.PollDelete.as_view(), name="poll_detail"),  # RESTful DELETE

    # Choices
    path("choices/", views.ChoiceListCreate.as_view(), name="choice_list"),
    path("choices/<int:pk>/", views.ChoiceDelete.as_view(), name="choice_detail"),  # RESTful DELETE
]