from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import CreateUserSerializer, UserDetailSerializer


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
