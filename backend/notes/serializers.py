# notes/serializers.py
from rest_framework import serializers
from .models import Note, NoteHistory, NotesUser, SharedNote
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer class for registering new users in the note-taking application.

    This serializer handles the registration process, including validation of email uniqueness
    and creation of user accounts.

    Fields:
        email (EmailField): The email address of the user. Required and must be unique.
        password (CharField): The password for the user account. Write-only.
        first_name (CharField): The first name of the user (optional).
        last_name (CharField): The last name of the user (optional).

    Methods:
        validate_email: Validates that the email address is unique.
        validate: Validates the data as a whole, setting the username to the email address.
        create: Creates a new user account with the provided validated data.
    """
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)


    class Meta:
        model = NotesUser
        fields = ('email', 'password', 'first_name', 'last_name')
    
    def validate_email(self, value):
        """
        Validates that the email address is unique.

        Args:
            value (str): The email address to validate.

        Returns:
            str: The validated email address.

        Raises:
            serializers.ValidationError: If the email address is not unique.
        """
        if NotesUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email must be unique")
        return value
    
    def validate(self, data):
        """
        Validates the data as a whole.

        Sets the username to the email address.

        Args:
            data (dict): The data to validate.

        Returns:
            dict: The validated data.
        """
        data["username"]= data.get('email')  # Set username to email
        return data

    def create(self, validated_data):
        """
        Creates a new user account with the provided validated data.

        Args:
            validated_data (dict): The validated data for creating the user account.

        Returns:
            NotesUser: The newly created user account.
        """
        user = NotesUser.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer class for user login in the note-taking application.

    This serializer handles the login process, including authentication of user credentials
    and generation of authentication tokens.

    Fields:
        username (CharField): The username of the user.
        password (CharField): The password for the user account.

    Methods:
        validate: Validates the provided username and password, authenticates the user,
            and generates an authentication token upon successful login.
    """
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        """
        Validates the provided username and password.

        Authenticates the user with the provided credentials and generates an authentication token
        upon successful login.

        Args:
            attrs (dict): The dictionary containing the username and password.

        Returns:
            dict: A dictionary containing the user's slug, name, token, and the authenticated user object.

        Raises:
            serializers.ValidationError: If the provided credentials are invalid or incomplete.
        """
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                # Combine first and last name to get user_name
                user_name = user.first_name + ' ' + user.last_name
                return {
                    'user_slug': user.userslug,
                    'user_name': user_name,
                    'token': token.key,
                    "user" : user
                }
            else:
                raise serializers.ValidationError('Unable to login with provided credentials')
        else:
            raise serializers.ValidationError('Both username and password are required')

# class AuthTokenSerializer(serializers.Serializer):
#     token = serializers.CharField()

class NoteSerializer(serializers.ModelSerializer):
    """
    Serializer class for note creation and modification in the note-taking application.

    This serializer validates and processes data related to creating and updating notes.
    It ensures that the provided user slug corresponds to an existing user and handles the
    creation and updating of note instances accordingly.

    Fields:
        user_slug (SlugField): The unique slug identifying the user who owns the note.
        content (CharField): The content of the note.

    Methods:
        validate_user_slug: Validates the provided user slug to ensure it corresponds to an existing user.
        create: Creates a new note instance with the provided user and content.
        update: Updates an existing note instance with the provided content.
    """
    user_slug = serializers.SlugField(required=True)
    content = serializers.CharField(required=True)

    class Meta:
        model = Note
        fields = ('user_slug', 'content')

    def validate_user_slug(self, value):
        """
        Validates the provided user slug to ensure it corresponds to an existing user.

        Args:
            value (str): The user slug to validate.

        Returns:
            str: The validated user slug.

        Raises:
            serializers.ValidationError: If no user exists with the provided slug.
        """
        # Check if user with the given slug exists
        # print("line 86",value)
        if not NotesUser.objects.filter(userslug=value).exists():
            raise serializers.ValidationError("User does not exist")
        return value
    
    def create(self, validated_data):
        """
        Creates a new note instance with the provided user and content.

        Args:
            validated_data (dict): The validated data containing user slug and content.

        Returns:
            Note: The newly created note instance.
        """
        # print(validated_data)
        user_slug = validated_data.get('user_slug')
        user    = NotesUser.objects.get(userslug=user_slug)
        content = validated_data.get("content")
        note = Note.objects.create(created_by_user=user, content=content, last_modified_by_user=user)
        return note
    
    # def update(self, instance, validated_data):
    #     """
    #     Updates an existing note instance with the provided content.

    #     Args:
    #         instance (Note): The note instance to be updated.
    #         validated_data (dict): The validated data containing the updated content.

    #     Returns:
    #         Note: The updated note instance.
    #     """
    #     instance.content = validated_data.get('content', instance.content)
    #     instance.save()
    #     return instance


class NoteViewSerializer(serializers.ModelSerializer):
    """
    Serializer class for viewing and updating notes in the note-taking application.

    This serializer handles the validation and processing of data for viewing and updating
    existing notes. It ensures that the provided user slug corresponds to an existing user
    and handles the update of note instances along with creating corresponding history records.

    Fields:
        slug (SlugField): The unique slug identifying the note.
        content (CharField): The content of the note.
        last_modified_by_user (SlugField): The user slug identifying the user who last modified the note.

    Methods:
        update: Updates an existing note instance with the provided content and user slug.
    """

    slug = serializers.SlugField(required=True)
    content = serializers.CharField(required=True)
    last_modified_by_user = serializers.SlugField(required=True, source="last_modified_by_user.userslug")

    class Meta:
        model = Note
        fields = ("slug", "content", "last_modified_by_user")

    def update(self, instance, validated_data):
        """
        Updates an existing note instance with the provided content and user slug.

        This method updates the content of an existing note instance with the content provided
        in the validated data. It also creates a corresponding history record to track the changes.

        Args:
            instance (Note): The note instance to be updated.
            validated_data (dict): The validated data containing the updated content and user slug.

        Returns:
            Note: The updated note instance after saving the changes.
        """
         
        print("inside update", validated_data)
        modified_user_slug = validated_data.get("last_modified_by_user")
        modified_user = NotesUser.objects.filter(userslug=modified_user_slug["userslug"])
        if modified_user.exists():
            original_content = instance.content
            instance.content = validated_data.get('content', instance.content)
            instance.last_modified_by_user = modified_user.first()
            instance.save()
            NoteHistory.objects.create(note=instance,
                                       original_content=original_content,
                                       updated_content=instance.content,
                                       updated_by_user=modified_user.first())
            return instance  # Return the updated instance after saving the changes
        else:
            # If modified user doesn't exist, raise validation error or handle it according to your requirements
            raise serializers.ValidationError("Invalid user slug provided.")


class NoteHistorySerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing note history records in the note-taking application.

    This serializer handles the conversion of NoteHistory model instances into JSON-compatible
    representations, including formatting the modified time field.

    Fields:
        note_slug (SlugField): The slug identifying the note associated with the history record.
        original_content (CharField): The original content of the note.
        updated_content (CharField): The updated content of the note.
        modified_by (EmailField): The email of the user who modified the note.
        modified_time (SerializerMethodField): The formatted timestamp of when the note was modified.

    Methods:
        get_modified_time: Retrieves the formatted modified time from the timestamp field.
    """
    note_slug = serializers.SlugField(source='note.slug')
    modified_by = serializers.EmailField(source='updated_by_user.email')
    modified_time = serializers.SerializerMethodField()

    class Meta:
        model = NoteHistory
        fields = ('note_slug', 'original_content', 'updated_content', 'modified_by', 'modified_time')

    def get_modified_time(self, obj):
        """
        Retrieves the formatted modified time from the timestamp field.

        This method extracts the timestamp from the NoteHistory instance and formats it
        as a human-readable string in the format 'dd-mm-yyyy at HH:MM AM/PM'.

        Args:
            obj (NoteHistory): The NoteHistory instance containing the timestamp.

        Returns:
            str: The formatted modified time string.
        """
        return obj.timestamp.strftime('%d-%m-%Y at %I:%M %p')



class SharedNoteSerializer(serializers.ModelSerializer):
    """
    Serializer class for serializing shared note instances in the note-taking application.

    This serializer handles the conversion of SharedNote model instances into JSON-compatible
    representations and supports creating new shared notes.

    Fields:
        note (SlugField): The slug identifying the note to be shared.
        shared_by (SlugField): The slug identifying the user sharing the note.
        shared_with (ListField): A list of slugs identifying the users with whom the note is shared.

    Methods:
        create: Handles the creation of a new shared note instance based on the provided data.
    """
    # print("line 106", "Inside Shared note Serializer")
    note = serializers.SlugField(required=True)
    shared_by = serializers.SlugField(required=True)
    shared_with = serializers.ListField(required=True)
    
    class Meta:
        model  = SharedNote
        fields = ("note", "shared_by", "shared_with") 


    def create(self, validated_data):
        """
        Handles the creation of a new shared note instance based on the provided data.

        This method creates a new SharedNote instance and associates it with the specified note,
        sharing user, and list of users with whom the note is shared.

        Args:
            validated_data (dict): The validated data for creating the shared note instance.

        Returns:
            SharedNote: The newly created shared note instance.
        """
        note_slug           = validated_data.get('note')
        shared_by_slug      = validated_data.get('shared_by')
        shared_with_slugs   = validated_data.get('shared_with', [])

        shared_note     = Note.objects.get(slug=note_slug)
        shared_by       = NotesUser.objects.get(userslug=shared_by_slug)
        
        shared_note_instance = SharedNote.objects.create(note=shared_note, shared_by=shared_by)
        
        for slug in shared_with_slugs:
            user = NotesUser.objects.filter(userslug=slug).first()
            if user:
                print(user)
                shared_note_instance.shared_with.add(user)
        
        shared_note_instance.save()
        return shared_note_instance
    
