from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Word(models.Model):
    kanji = models.CharField(max_length=64)
    gana = models.CharField(max_length=64)
    tone = models.CharField(max_length=8)
    chn = models.CharField(max_length=128)
    type = models.CharField(max_length=16) #词型
    related_audio = models.CharField(max_length=128)

    def __str__(self):
        return self.kanji;

class Book(models.Model):
    name = models.CharField(max_length=128)
    author = models.CharField(max_length=64)
    words = models.ManyToManyField(Word)

class Realuser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='realuser')
    books = models.ManyToManyField(Book)
    hate_words = models.ManyToManyField(Word)

@receiver(post_save, sender=User)
def create_real_user(sender, instance, created, **kwargs):
    if created:
        Realuser.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_real_user(sender, instance, created, **kwargs):
    instance.realuser.save()
