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

class ChoiceSerializer(serializers.ModelSerializer):
    vote_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Choice
        fields = ["id", "choice_text", "vote_count", "poll", "created_at", "updated_at"]
        read_only_fields = ["id", "vote_count", "created_at", "updated_at", "poll"]  #
    def get_vote_count(self, obj):
        return obj.voters.count()


class PollSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Poll
        fields = ["id", "question", "status", "created_at", "updated_at", "user", "choices"]
        extra_kwargs = {"user": {"read_only": True}}

    def validate_choices(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("A poll must have at least two choices.")
        return value

    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        poll = Poll.objects.create(**validated_data)
        for choice_data in choices_data:
            # Set poll explicitly here
            Choice.objects.create(poll=poll, choice_text=choice_data['choice_text'])
        return poll

    def update(self, instance, validated_data):
        choices_data = validated_data.pop("choices", [])
        instance.question = validated_data.get("question", instance.question)
        instance.status = validated_data.get("status", instance.status)
        instance.save()

        existing_choices = {c.id: c for c in instance.choices.all()}
        incoming_ids = []

        for choice_data in choices_data:
            choice_id = choice_data.get("id", None)

            if choice_id and choice_id in existing_choices:
                # Update existing
                choice = existing_choices[choice_id]
                choice.choice_text = choice_data["choice_text"]
                choice.save()
                incoming_ids.append(choice_id)
            else:
                # Create new
                new_choice = Choice.objects.create(poll=instance, **choice_data)
                incoming_ids.append(new_choice.id)

        # Delete removed choices
        for choice_id, choice_obj in existing_choices.items():
            if choice_id not in incoming_ids:
                choice_obj.delete()

        return instance