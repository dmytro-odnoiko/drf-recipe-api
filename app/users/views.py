"""
Views for the user API.
"""

from rest_framework import generics, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from users.models import Profile
from users.permissions import IsOwnerOrReadOnly
from users.serializers import (AuthTokenSerializer, ProfileSerializer,
                               UserSerializer)

from core.tasks import send_registered_emails

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        created = super().create(request, *args, **kwargs)
        if created.status_code == status.HTTP_201_CREATED:
            send_registered_emails.delay(emails=[created.data.get('email')])
        
        return created

class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user


class ProfileView(generics.GenericAPIView):
    """View and update user profile."""
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, pk, format=None):
        profile = Profile.objects.get(pk=pk)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        profile = Profile.objects.get(pk=pk)
        serializer = ProfileSerializer(
            profile,
            data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
