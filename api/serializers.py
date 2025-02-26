from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Poll


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = ["id", "question", "status", "created_at","updated_at", "user"]
        extra_kwargs = {"user": {"read_only": True}}