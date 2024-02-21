# app/urls.py
from django.urls import path
from .views import (UserRegistrationAPIView, UserLoginAPIView, NoteCreateAPIView,
                    NoteDetailAPIView, NoteVersionHistoryAPIView, SharedNoteAPIView, UserLogoutAPIView)

"""
/signup/: Maps to the UserRegistrationAPIView for user registration.
/login/: Maps to the UserLoginAPIView for user login.
/logout/: Maps to the UserLogoutAPIView for user logout.
/notes/create/: Maps to the NoteCreateAPIView for creating a new note.
/notes/share/: Maps to the SharedNoteAPIView for sharing a note with other users.
/notes/<str:slug>/: Maps to the NoteDetailAPIView for retrieving and updating a specific note.
/notes/version-history/<str:slug>/: Maps to the NoteVersionHistoryAPIView for retrieving the version history of a specific note
"""
urlpatterns = [
    path('signup/', UserRegistrationAPIView.as_view(), name='user_registration'),
    path('login/', UserLoginAPIView.as_view(), name='user_login'),
    path('logout/', UserLogoutAPIView.as_view(), name='user_logout'),

    path('notes/create/', NoteCreateAPIView.as_view(), name='create_note'),
    path('notes/share/', SharedNoteAPIView.as_view(), name='share_note'),
    path('notes/<str:slug>/', NoteDetailAPIView.as_view(), name='note_detail'),
    path('notes/version-history/<str:slug>/', NoteVersionHistoryAPIView.as_view(), name='note_version_history'),
    # Add other endpoints here
]
