from django.urls import path
from . import views


urlpatterns = [
    path("polls/",views.PollListCreate.as_view(), name="polls_list"),
    path("polls/delete/<int:pk>/",views.PollDelete.as_view(), name="delete_delete"),
]