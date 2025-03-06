from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer, PollSerializer, ChoiceSerializer, ProfileSerializer
from .models import Poll, Choice, CustomUser, Profile
from rest_framework.response import Response
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def register_user(request):
#     # User registration API that prevents duplicate emails and creates a profile automatically.
#     email = request.data.get('email')

#     # Check if a user with this email already exists
#     if CustomUser.objects.filter(email=email).exists():
#         return Response(
#             {'error': 'A user with this email already exists.'},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     # Proceed with registration if email is unique
#     serializer = UserSerializer(data=request.data)
#     if serializer.is_valid():
#         user = serializer.save()  # Save user instance
#         Profile.objects.create(user=user)  # Create profile for the new user
        
#         return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Create User View
# class CreateUserView(generics.CreateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AllowAny]

# -----------------------------
# User Registration View
# -----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    # Registers a new user if email is unique.
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()  # Profile is automatically created in `CustomUser.save()`
        return Response(
            {"message": "User registered successfully", "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------
# Profile View (Get, Update, Delete)
# -----------------------------
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    # Allows authenticated users to view, update, or delete their own profile.
    profile = request.user.profile  # Ensures users can only access their own profile

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        profile.delete()
        return Response({"message": "Profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
# Create & List Polls
class PollListCreate(generics.ListCreateAPIView):
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Poll.objects.filter(user=self.request.user)
    
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)  # Automatically assigns the user

    def perform_create(self, serializer):
        # Save the new poll
        poll = serializer.save(user=self.request.user)

        # Send real-time WebSocket notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "poll_updates",
            {
                "type": "broadcast_poll",
                "poll": PollSerializer(poll).data,  # Serialize poll data
            },
        )

        return Response(PollSerializer(poll).data)

# Delete Poll
class PollDelete(generics.DestroyAPIView):
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Poll.objects.filter(user=self.request.user)  # Only allow the owner to delete

# Create & List Choices
class ChoiceListCreate(generics.ListCreateAPIView):
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Choice.objects.filter(poll__user=self.request.user)  # Fixed filtering

    def perform_create(self, serializer):
        serializer.save()  # No need for `is_valid()`, DRF handles it

# Delete Choice
class ChoiceDelete(generics.DestroyAPIView):
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Choice.objects.filter(poll__user=self.request.user)  # Fixed filtering