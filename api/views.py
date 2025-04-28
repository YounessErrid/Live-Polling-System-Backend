from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import generics, status
from .serializers import UserSerializer, PollSerializer, ChoiceSerializer
from .models import Poll, Choice, CustomUser

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Create User View
class CreateUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

# -----------------
# GET All Polls
# -----------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_polls(request):
    polls = Poll.objects.filter(user=request.user)
    serializerData = PollSerializer(polls, many=True).data
    return Response(serializerData)

# -----------------
# Post Poll
# -----------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_poll(request):
    data = request.data
    data['user'] = request.user.id  # Assign the authenticated user

    serializer = PollSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ------------------------
# GET, PUT, DELETE Poll
# ------------------------
@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticated])
def poll_detail(request, pk):
    try:
        poll = Poll.objects.get(pk=pk)
    except Poll.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    # Ensure user can only update/delete their own polls
    if request.method in ['PUT', 'DELETE'] and poll.user != request.user:
        return Response({"error": "You are not authorized to modify this poll"}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = PollSerializer(poll)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        poll.delete()
        return  Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'PUT':
        data = request.data 
        data['user'] = request.user.id  # Ensure the user field is not changed
        serializer = PollSerializer(poll, data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors ,status=status.HTTP_400_BAD_REQUEST)

# -----------------
# POST Choice
# -----------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_choice(request):
    data = request.data 
    # Ensure poll_id is provided
    poll_id = data.get('poll')
    if not poll_id:
        return Response({"error": "Poll ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get the poll instance
    try:
        poll = Poll.objects.get(id=poll_id)
    except Poll.DoesNotExist:
        return Response({"error": "Poll not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Ensure user is the owner of the poll
    if poll.user != request.user:
        return Response({"error": "You are not authorized to add choices to this poll"}, status=status.HTTP_403_FORBIDDEN)

    data['poll'] = poll.id  # Ensure poll is correctly assigned
    serializer = ChoiceSerializer(data=data)
    if serializer.is_valid():
        serializer.save(poll=poll)  # Pass the poll instance explicitly
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ------------------------
# GET, PUT, DELETE Choice
# ------------------------
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def choice_detail(request, pk):
    try:
        choice = Choice.objects.get(pk=pk)
    except Choice.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    # Ensure user can only update/delete choices from their own polls
    if request.method in ['PUT', 'DELETE'] and choice.poll.user != request.user:
        return Response({"error": "You are not authorized to modify this choice"}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = ChoiceSerializer(choice)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        choice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'PUT':
        data = request.data 
        data['poll'] = request.poll.id 
        serializer = ChoiceSerializer(choice, data=data)
        if serializer.is_valid():
            serializer.save(poll=request.poll)
            return Response(serializer.data)
        return Response(serializer.errors ,status=status.HTTP_400_BAD_REQUEST)
    
