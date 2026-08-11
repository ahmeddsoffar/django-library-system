from rest_framework import generics,permissions
from .serializers import RegisterSerializer
from rest_framework.throttling import ScopedRateThrottle

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"