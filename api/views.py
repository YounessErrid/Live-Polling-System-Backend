from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer, PollSerializer, ChoiceSerializer
from .models import Poll, Choice, CustomUser

# ✅ Create User View
class CreateUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

# ✅ Create & List Polls
class PollListCreate(generics.ListCreateAPIView):
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Poll.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # ✅ Automatically assigns the user

# ✅ Delete Poll
class PollDelete(generics.DestroyAPIView):
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Poll.objects.filter(user=self.request.user)  # ✅ Only allow the owner to delete

# ✅ Create & List Choices
class ChoiceListCreate(generics.ListCreateAPIView):
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Choice.objects.filter(poll__user=self.request.user)  # ✅ Fixed filtering

    def perform_create(self, serializer):
        serializer.save()  # ✅ No need for `is_valid()`, DRF handles it

# ✅ Delete Choice
class ChoiceDelete(generics.DestroyAPIView):
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Choice.objects.filter(poll__user=self.request.user)  # ✅ Fixed filtering