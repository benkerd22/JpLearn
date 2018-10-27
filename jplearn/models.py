from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Word(models.Model):
    kanji = models.CharField(max_length=32)
    gana = models.CharField(max_length=32)
    tone = models.CharField(max_length=8)
    chn = models.CharField(max_length=64)

    def __str__(self):
        return self.kanji;

class Realuser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='realuser')
    liked_words = models.ManyToManyField(Word)

@receiver(post_save, sender=User)
def create_real_user(sender, instance, created, **kwargs):
    if created:
        Realuser.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_real_user(sender, instance, created, **kwargs):
    instance.realuser.save()
