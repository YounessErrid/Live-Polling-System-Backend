from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Poll


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        # set password to be write only, and never read it when getting user infos
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = ["id", "question", "status", "created_at","updated_at", "user"]
        extra_kwargs = {"user": {"read_only": True}}