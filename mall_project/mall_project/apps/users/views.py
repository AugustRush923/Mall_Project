from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import *
from rest_framework_jwt.views import ObtainJSONWebToken

from .serializers import *
from .models import User
from goods.serializers import SKUSerializer
from mall_project.utils.constants import USER_ADDRESS_COUNTS_LIMIT
from mall_project.utils.merge_cart_cookie_to_redis import merge_cart_cookie_to_redis


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
        """
        覆写父方法，默认父方法根据pk值去filter queryset
        业务需要获取当前用户信息。
        """
        return self.request.user


class PasswordUpdateView(UpdateAPIView):
    serializer_class = UpdatePasswordSerializer
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


# url(r'^browse_histories/$', views.UserBrowsingHistoryView.as_view()),
class UserBrowsingHistoryView(CreateModelMixin, GenericAPIView):
    """
    用户浏览历史记录
    """
    serializer_class = AddUsersHistorySerializer
    permission_classes = [IsAuthenticated]

    # 以GET请求访问browse_histories/
    def get(self, request):
        user_id = request.user.id
        # 获取history Redis中 history_user_id的所有elements
        history = get_redis_connection('history').lrange(f"history_{user_id}", 0, -1)
        '''
        skus = []
        for sku_id in history:
            sku = SKU.objects.get(id=sku_id)
            skus.append(sku)
        '''
        # 组装history列表 使用列表生成式
        skus = [SKU.objects.get(id=sku_id) for sku_id in history]
        s = SKUSerializer(skus, many=True)
        return Response(s.data)

    def post(self, request):
        # CreateModelMixin里的save方法以使用Serializer里的create方法
        return self.create(request)


class UserAuthorizeView(ObtainJSONWebToken):

    def post(self, request, *args, **kwargs):
        response = super(UserAuthorizeView, self).post(request, *args, **kwargs)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            response = merge_cart_cookie_to_redis(request, user, response)
        return response
