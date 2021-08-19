from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import *

from .serializers import *
from .models import User
from .constants import USER_ADDRESS_COUNTS_LIMIT


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


class PasswordUpdateView(UpdateAPIView):
    serializer_class = UpdatePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        print(request.data)
        return super(PasswordUpdateView, self).update(request, *args, **kwargs)


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


class AddressViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.address.filter(is_delete=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            "limit": USER_ADDRESS_COUNTS_LIMIT,
            'address': serializer.data
        })

    # POST /address/
    def create(self, request, *args, **kwargs):
        count = request.user.address.count()
        if count >= USER_ADDRESS_COUNTS_LIMIT:
            return Response({"message": "保存地址已经达到上限"}, status=HTTP_400_BAD_REQUEST)
        return super(AddressViewSet, self).create(request, *args, **kwargs)

    # delete /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        address = self.get_object()
        address.is_delete = True
        address.save()
        return Response({'message': "ok"}, status=HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    def status(self, request, pk=None, *args, **kwargs):
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({"message": "ok"}, status=HTTP_200_OK)

    # put /addresses/pk/title/
    def title(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
