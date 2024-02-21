# Create your models here.
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager   # Import the default User Manager
from django.contrib.auth.models import User


class NotesManager(UserManager):
    """
    Custom manager for the NotesUser model.
    """
    pass 


class NotesUser(AbstractUser):
    """
    Note model representing users in the note-taking application.

    Inherits from Django's AbstractUser model and includes additional fields.

    Fields:
        userslug (SlugField): A unique identifier for the user.
        email (EmailField): The email address of the user.
        first_name (CharField): The first name of the user.
        last_name (CharField): The last name of the user.

    Methods:
        save: Override save method to generate a random slug if not provided.
        generate_random_slug: Helper method to generate a random hexadecimal string for the slug.
        __str__: String representation of a user object.
    """
    userslug = models.SlugField(primary_key=True,unique=True, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=30)  # Add first name field
    last_name = models.CharField(max_length=30)   # Add last name field

    objects = NotesManager()
    
    def save(self, *args, **kwargs):
        """
        Override the save method to generate a random slug if not provided.
        """
        if not self.userslug:
            self.userslug = self.generate_random_slug()[:10]  # Generate random slug
        super().save(*args, **kwargs)

    def generate_random_slug(self):
        """
        Helper method to generate a random hexadecimal string for the slug.

        Returns:
            str: Random hexadecimal string.
        """
        return uuid.uuid4().hex  # Generate random hexadecimal string 

    def __str__(self):
        """
        String representation of a user object.

        Returns:
            str: The email address of the user.
        """
        return self.email   


class Note(models.Model):
    """
    Model representing a note in the note-taking application.

    Each note belongs to a single user and contains content.

    Fields:
        slug (SlugField): A unique identifier for the note.
        created_by_user (ForeignKey): The user who created the note.
        last_modified_by_user (ForeignKey): The user who last modified the note.
        content (TextField): The content of the note.
        created_at (DateTimeField): The date and time when the note was created.

    Methods:
        __str__: String representation of a note object.
        save: Override save method to generate a random slug if not provided.
        generate_random_slug: Helper method to generate a random hexadecimal string for the slug.
    """
    slug = models.SlugField(unique=True, null=False, blank=False)
    created_by_user = models.ForeignKey(NotesUser, on_delete=models.CASCADE, related_name='created_user')
    last_modified_by_user = models.ForeignKey(NotesUser, on_delete=models.CASCADE, related_name='last_modified_user')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String representation of a note object.

        Returns:
            str: A string representing the content of the note.
        """
        return self.content
    
    def save(self, *args, **kwargs):
        """
        Override the save method to generate a random slug if not provided.
        """
        if not self.slug:
            self.slug = self.generate_random_slug()[:9]  # Generate random slug
        super().save(*args, **kwargs) 
    
    def generate_random_slug(self):
        """
        Helper method to generate a random hexadecimal string for the slug.

        Returns:
            str: Random hexadecimal string.
        """
        return uuid.uuid4().hex  # Generate random hexadecimal string 
    

class SharedNote(models.Model):
    """
    Model representing a shared note in the note-taking application.

    A shared note is created when a user shares a note with one or more other users.

    Fields:
        note (ForeignKey): The note that is being shared.
        shared_by (ForeignKey): The user who is sharing the note.
        shared_with (ManyToManyField): The users with whom the note is being shared.
        shared_at (DateTimeField): The date and time when the note was shared.

    Methods:
        __str__: String representation of a shared note object.
    """
    
    note = models.ForeignKey(Note, on_delete=models.CASCADE, null=False, blank=False)
    shared_by = models.ForeignKey(NotesUser, on_delete=models.CASCADE, related_name='shared_user',  null=False, blank=False)
    shared_with = models.ManyToManyField(NotesUser, related_name='received_users', blank=False)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String representation of a shared note object.

        Returns:
            str: A string containing information about the shared note.
        """
        return f"{self.note} shared by {self.shared_by} with {', '.join([user.username for user in self.shared_with.all()])} at {self.shared_at}"

class NoteHistory(models.Model):
    """
    Model representing the history of changes made to a note in the note-taking application.

    Each instance of this model represents a specific change made to a note, capturing the original
    content, updated content, the user who made the change, and the timestamp of the change.

    Fields:
        note (ForeignKey): The note for which the change history is recorded.
        original_content (TextField): The original content of the note before the change.
        updated_content (TextField): The updated content of the note after the change.
        updated_by_user (ForeignKey): The user who made the change to the note.
        timestamp (DateTimeField): The date and time when the change was made.

    Methods:
        formatted_timestamp: Returns a formatted string representing the timestamp in the format 'dd-mm-yyyy at hh:mm AM/PM'.
    """

    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='history')
    original_content = models.TextField()
    updated_content = models.TextField()
    updated_by_user = models.ForeignKey(NotesUser, on_delete=models.CASCADE, related_name='updated_notes', null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def formatted_timestamp(self):
        """
        Returns a formatted string representing the timestamp.

        Returns:
            str: A string representing the timestamp in the format 'dd-mm-yyyy at hh:mm AM/PM'.
        """
        return self.timestamp.strftime('%d-%m-%Y at %I:%M %p')