from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView, Response
from .serializers import RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LogoutSerializer
import rest_framework.status as status


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []

class MeView(RetrieveAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

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