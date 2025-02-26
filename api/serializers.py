from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Poll, Choice

User = get_user_model()

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(email=validated_data['email'])
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user

# Poll Serializer
class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = ["id", "question", "status", "created_at", "updated_at", "user"]
        extra_kwargs = {"user": {"read_only": True}}  # Auto-assigned from request.user

# Choice Serializer
class ChoiceSerializer(serializers.ModelSerializer):
    voters = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )
    vote_count = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = ["id", "choice_text", "voters", "vote_count", "created_at", "updated_at", "poll"]

    def get_vote_count(self, obj):
        return obj.voters.count()