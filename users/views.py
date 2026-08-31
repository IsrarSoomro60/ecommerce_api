from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView, Response
from .serializers import RegisterSerializer
from rest_framework.permissions import IsAuthenticated


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []

class MeView(RetrieveAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LogoutSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
        except Exception:
            return Response(
                {'success': False, 'message': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'success': True, 'message': 'Logout successful'},
            status=status.HTTP_205_RESET_CONTENT
        )    