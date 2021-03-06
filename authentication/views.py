from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import User
from authentication.serializers import UserSerializer


class RegistrationAPIView(CreateAPIView):

    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class LogInAPIView(APIView):

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        if (email and password) is not None:
            user = authenticate(email=email, password=password)
            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key})
        return Response({'details': 'Credentials are invalid.'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(RetrieveAPIView):

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        return self.queryset.get(pk=self.request.user.pk)


class AllUsersAPIView(ListAPIView):

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, ]
