from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
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

class Comments(models.Model):
    content=models.CharField(max_length=140)
    create_time=models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    whichkwik=models.ForeignKey(Kwik, on_delete=models.CASCADE)

class MyProfile(models.Model):
    aboutme=models.CharField(max_length=140, null=True, default="brak opisu")
    myphonenumber=models.IntegerField(null=True)
    myuicolour=models.CharField(max_length=64, default="59, 126, 219")
    location=models.CharField(max_length=30, null=True)
    issecret=models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            MyProfile.objects.create(user=instance)
