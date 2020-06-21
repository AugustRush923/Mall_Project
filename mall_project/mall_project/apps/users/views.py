from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from .serializers import CreateUserSerializer


class UserView(CreateAPIView):
    """
    用户注册
    传入参数：
        username, password, password2, sms_code, mobile, allow
    """
    serializer_class = CreateUserSerializer
