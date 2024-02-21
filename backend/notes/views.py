# app/views.py
from rest_framework import generics, status

from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Note, NoteHistory, NotesUser, SharedNote
from .serializers import (UserRegistrationSerializer, UserLoginSerializer,
                          NoteSerializer, NoteHistorySerializer, NoteViewSerializer, SharedNoteSerializer)
from rest_framework.authentication import TokenAuthentication

class UserRegistrationAPIView(generics.CreateAPIView):
    """
    API endpoint for user registration.

    This view provides an endpoint for registering new users in the note-taking application.
    Users can submit their registration information via a POST request to this endpoint.

    Attributes:
        queryset (QuerySet): The queryset for retrieving NoteUser instances.
        serializer_class (Serializer): The serializer class to use for validating user registration data.

    Methods:
        create: Handles POST requests for user registration.
    """
    queryset = NotesUser.objects.all()                 # Queryset for retrieving Note Users.
    serializer_class = UserRegistrationSerializer      # Specify serializer to validate user registration data.

    def create(self, request, *args, **kwargs):
        """
        Handle POST requests for user registration.

        This method validates the data provided in the request payload using the serializer.
        If the data is valid, it creates a new user instance and returns a success response.
        If the data is invalid, it returns an error response indicating the validation errors.

        Args:
            request (Request): The HTTP request object containing user registration data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: A JSON response indicating the success or failure of user registration.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": "User created successfully. :)", "data":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Unable to register a User successfully. !", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST )


class UserLoginAPIView(generics.CreateAPIView):
    """
    API endpoint for user login.

    This view provides an endpoint for users to log in to the note-taking application.
    Users can submit their login credentials via a POST request to this endpoint.

    Attributes:
        serializer_class (Serializer): The serializer class to use for validating user login data.

    Methods:
        post: Handles POST requests for user login.
    """

    serializer_class = UserLoginSerializer       # Specify serializer for to validate user login data.
    
    def post(self, request):
        """
        Handle POST requests for user login.

        This method validates the login data provided in the request payload using the serializer.
        If the data is valid, it logs in the user and returns a success response.
        If the data is invalid, it returns an error response indicating the validation errors.

        Args:
            request (Request): The HTTP request object containing user login data.

        Returns:
            Response: A JSON response indicating the success or failure of user login.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data.pop("user")
            login(request, user)
            response_data = serializer.validated_data
            return Response({"message": "User: {first_name} {last_name} login successfully.:)".format(first_name=user.first_name, last_name=user.last_name),
                             "data":response_data }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User not login successfully. !",
                             "errors": serializer.errors }, status=status.HTTP_200_OK)


class UserLogoutAPIView(APIView):
    """
    API endpoint for user logout.

    This view provides an endpoint for users to log out of the note-taking application.
    Users must be authenticated to access this endpoint.

    Attributes:
        permission_classes (list): The list of permission classes required to access this endpoint.

    Methods:
        get: Handles GET requests for user logout.
    """
    permission_classes = [IsAuthenticated,]

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for user logout.

        This method logs out the authenticated user and revokes their authentication token.
        If the user is already logged out or not authenticated, it returns a success response.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: A JSON response indicating the success of user logout.
        """

        if request.user.is_authenticated:
            print(request.user)
            if hasattr(request.user, 'auth_token'):
                # Delete the user's authentication token and log them out
                request.user.auth_token.delete()
                logout(request)
                return Response({"message": "User logout successfully :)"}, status=status.HTTP_200_OK)
        else:
            # If the user is already logged out or not authenticated, return a success response
            return Response({"message": "User already logout successfully !"}, status=status.HTTP_200_OK)


class NoteCreateAPIView(generics.CreateAPIView):
    """
    API endpoint for creating a new note.

    This view provides an endpoint for authenticated users to create a new note in the note-taking application.
    Users must be authenticated to access this endpoint.

    Attributes:
        queryset (QuerySet): The queryset for retrieving notes.
        permission_classes (list): The list of permission classes required to access this endpoint.
        authentication_classes (list): The list of authentication classes used for authentication.
        serializer_class (Serializer): The serializer class used to validate Note creation data.

    Methods:
        create: Handles POST requests for creating a new note.
    """

    queryset = Note.objects.all()            # Queryset for retrieving notes
    permission_classes = [IsAuthenticated,]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    serializer_class = NoteSerializer        # Specify serializer to validate Note creation data.
   
    def create(self, request, *args, **kwargs):
        """
        Handle POST requests for creating a new note.

        This method validates the request data using the serializer, creates a new note,
        and returns a JSON response indicating the success or failure of note creation.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: A JSON response indicating the success or failure of note creation.
        """

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": "Note created successfully :)", "data":serializer.validated_data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Failed to create Note !", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

class NoteDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating a note.

    This view provides an endpoint for authenticated users to retrieve and update a specific note in the note-taking application.
    Users must be authenticated to access this endpoint.

    Attributes:
        queryset (QuerySet): The queryset for retrieving notes.
        serializer_class (Serializer): The serializer class used to get/validate note detail data.
        lookup_field (str): The lookup field for retrieving notes by slug.
        permission_classes (list): The list of permission classes required to access this endpoint.
        authentication_classes (list): The list of authentication classes used for authentication.

    Methods:
        retrieve: Handles GET requests for retrieving a note.
    """


    queryset = Note.objects.all()               # Queryset for retrieving notes
    serializer_class = NoteViewSerializer       # Specify serializer for get/validate note detail data.
    lookup_field = 'slug'                       # Lookup field for retrieving notes by slug 
    permission_classes = [IsAuthenticated,]     # Allow if user is Autheticated
    authentication_classes = [TokenAuthentication, SessionAuthentication] # Authentication classes for the view
    
    def retrieve(self, request, *args, **kwargs):
        """
        Handle GET requests for retrieving a note.

        This method retrieves a specific note object based on the provided slug, serializes it using the serializer,
        and returns a JSON response indicating the success or failure of note retrieval.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: A JSON response indicating the success or failure of note retrieval.
        """
        # print(kwargs)
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response({"message": "Note found", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Note not found", "errors":serializer.errors}, status=status.HTTP_404_NOT_FOUND) 


    def update(self, request, *args, **kwargs):
        """
        Handle PUT requests for updating a note.

        This method retrieves the note object to be updated, validates the request data using the serializer,
        updates the note, and returns a JSON response indicating the success or failure of note update.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: A JSON response indicating the success or failure of note update.
        """
        instance = self.get_object()
        # print(instance, request.data, "line 74")
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Note updated successfully. :)", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Failed to update note. !", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class SharedNoteAPIView(generics.CreateAPIView):
    """
    API endpoint for sharing a note with other users.

    This view provides an endpoint for authenticated users to share a note with other users in the note-taking application.
    Users must be authenticated to access this endpoint.

    Attributes:
        queryset (QuerySet): The queryset for retrieving shared notes.
        serializer_class (Serializer): The serializer class used to validate sharing note data.
        permission_classes (list): The list of permission classes required to access this endpoint.
        authentication_classes (list): The list of authentication classes used for authentication.

    Methods:
        create: Handles POST requests for sharing a note with other users.
    """
    queryset = SharedNote.objects.all()             # Queryset for retrieving Sharednotes.
    serializer_class = SharedNoteSerializer         # Specify serializer to validate sharing notes data.
    permission_classes = [IsAuthenticated,]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def create(self, request, *args, **kwargs):
        """
        Handle POST requests for sharing a note with other users.

        This method validates the request data using the serializer,
        creates a new shared note, and returns a JSON response indicating the success or failure of note sharing.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: A JSON response indicating the success or failure of note sharing.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            print("line 44",serializer.validated_data)
            # serializer.save()
            self.perform_create(serializer)
            return Response({"message": "Note Shared successfull. :)", "data":serializer.validated_data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Failed to Share Note !", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class NoteVersionHistoryAPIView(generics.ListAPIView):
    """
    API endpoint for retrieving the version history of a note.

    This view provides an endpoint for authenticated users to retrieve the version history of a specific note in the note-taking application.
    Users must be authenticated to access this endpoint.

    Attributes:
        queryset (QuerySet): The queryset for retrieving note history.
        serializer_class (Serializer): The serializer class used to serialize note history data.
        permission_classes (list): The list of permission classes required to access this endpoint.
        authentication_classes (list): The list of authentication classes used for authentication.

    Methods:
        get: Handles GET requests for retrieving the version history of a note.
    """
    queryset = NoteHistory.objects.all()        # Queryset for retrieving note history
    serializer_class = NoteHistorySerializer    # Specify serializer to get note history data.
    permission_classes = [IsAuthenticated,]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
