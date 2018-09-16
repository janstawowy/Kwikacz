from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Kwik(models.Model):
    content=models.CharField(max_length=140)
    create_time=models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class Messages(models.Model):
    content=models.TextField(null=True)
    towho=models.ForeignKey(User, on_delete=models.CASCADE, related_name="adresat")
    fromwho=models.ForeignKey(User, on_delete=models.CASCADE, related_name="nadawca")
    seen=models.BooleanField(default=False)
    date_sent=models.DateTimeField(auto_now_add=True)