from rest_framework import serializers
from .models import Poll, Choice, Profile, CustomUser

# -------------------------
# Profile Serializer
# -------------------------
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

# -------------------------
# User Serializer
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)  # Include profile data in response

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'profile']  # Include profile
        extra_kwargs = {'password': {'write_only': True}}  # Hide password in response

    def validate_email(self, value):
        # Ensure email is unique
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # Create user with hashed password
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # Hash password
        user.save()
        return user

# -------------------------
# Poll Serializer
# -------------------------
class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = ["id", "question", "status", "created_at", "updated_at", "user"]
        extra_kwargs = {"user": {"read_only": True}}  # Auto-assigned from request.user

# -------------------------
# Choice Serializer
# -------------------------
class ChoiceSerializer(serializers.ModelSerializer):
    voters = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CustomUser.objects.all(), required=False
    )
    vote_count = serializers.SerializerMethodField()

    class Meta:
        model = Choice
        fields = ["id", "choice_text", "voters", "vote_count", "created_at", "updated_at", "poll"]

    def get_vote_count(self, obj):
        return obj.voters.count()