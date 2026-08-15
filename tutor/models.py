from django.db import models 
# Create your models here.
from django.contrib.auth.models import User

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} - {self.user.username}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} - {self.content[:30]}"

class UserProfile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    trial_start = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    message_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"