from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import *
from .serializers import CreateUserSerializer, UserDetailSerializer, EmailSerializer
from .models import User


class UserView(CreateAPIView):
    """
    用户注册
    传入参数：
        username, password, password2, sms_code, mobile, allow
    """
    serializer_class = CreateUserSerializer


class UserDetailView(RetrieveAPIView):
    """
    id	int	是	用户id
    username	str	是	用户名
    mobile	str	是	手机号
    email	str	是	email邮箱
    email_active	bool	是	邮箱是否通过验证
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmailUpdateView(UpdateAPIView):
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class VerifyEmailView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({'message': "缺少token"}, status=HTTP_400_BAD_REQUEST)
        print(token)
        user = User.check_verify_email_token(token)
        if not user:
            return Response({'message': "链接信息无效"}, status=HTTP_400_BAD_REQUEST)
        user.email_active = True
        user.save()
        return Response({'message': "OK"})
