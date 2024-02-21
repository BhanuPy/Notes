from django.contrib import admin
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import NotesUser, Note, NoteHistory, SharedNote
# User = get_user_model()
admin.site.register(NotesUser)
admin.site.register(Note)
admin.site.register(NoteHistory)
admin.site.register(SharedNote)