from django.contrib import admin
from .models import Realuser, Book, Word

# Register your models here.

admin.site.register(Realuser)
admin.site.register(Book)
admin.site.register(Word)
