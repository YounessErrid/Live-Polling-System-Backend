from django.urls import path
from . import views


urlpatterns = [
    path("polls/",views.PollListCreate.as_view(), name="polls_list"),
    path("polls/<int:pk>/delete/", views.PollDelete.as_view(), name="delete_poll"),
    path("choices/",views.ChoiceListCreate.as_view(), name="choice_list"),
    path("choices/<int:pk>/delete/", views.ChoiceDelete.as_view(), name="delete_choice"),
]