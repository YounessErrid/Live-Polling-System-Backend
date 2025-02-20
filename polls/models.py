from django.db import models
from django.contrib.auth.models import User

# Poll.
class Poll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    question = models.CharField(max_length=300)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    # deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return self.question

#Choice Model:
class Choice(models.Model):
    choice_text = models.CharField(max_length=300)
    voters = models.ManyToManyField(User, related_name="voted_choices", blank=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="choices")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
            return self.choice_text