from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Chat (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats")
    subject = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id} ({self.subject}) - {self.user.username}"
    

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_bot = models.BooleanField(default=False)
    sequence = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Message {self.id} in Chat {self.chat.id} - {self.sender.username}"
    
    class Meta:
        ordering = ['sequence']