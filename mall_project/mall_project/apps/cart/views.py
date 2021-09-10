import pickle
import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_redis import get_redis_connection
# Create your views here.

from cart.serializer import CartSerializer, CartSKUSerializer, CartDeleteSerializer, CartSelectAllSerializer
from goods.models import SKU
from mall_project.utils.constants import CART_COOKIE_EXPIRES


class CartView(APIView):
    """
    购物车
    """

    def get_user(self, request):
        try:
            user = request.user
        except Exception:
            user = None
        return user

    def perform_authentication(self, request):
        """
        重写父类的用户验证方法，不在进入视图前就检查JWT
        """

    def get(self, request):
        # try:
        #     # 尝试检查JWT
        #     user = request.user
        # except Exception:
        #     # 如果未通过JWT，则代表为匿名用户
        #     user = None
        user = self.get_user(request)

        if user is not None and user.is_authenticated:  # 判断 如果认证通过 则进行认证用户逻辑
            redis_conn = get_redis_connection('cart')
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)  # 获取当前用户的hash中的所有值
            redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)  # 获取set中的所有值
            cart = {}
            for sku_id, count in redis_cart.items():  # {sku_id: count, sku_id: count}
                cart[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_cart_selected
                }  # 组装购物车字典  cart = {sku_id: {'count': count, 'selected': selected}}
        else:  # 反之， 则进行匿名用户逻辑
            cart = request.COOKIES.get('cart')  # 获取cookie值
            if cart is not None:
                # 字符串 --> bytes字符串 --> bytes --> Python dict
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}
        skus = SKU.objects.filter(id__in=cart.keys())  # sku_id
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']
        serializer = CartSKUSerializer(skus, many=True)  # 序列化
        return Response(serializer.data)

    def post(self, request):
        """
        添加购物车
        """
        # 创建序列化器
        serializer = CartSerializer(data=request.data)
        # 调用is_valid进行校验
        serializer.is_valid(raise_exception=True)
        # 获取校验后的数据
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        # 尝试对请求的用户进行验证
        # try:
        #     user = request.user
        # except Exception:
        #     # 验证失败，用户未登录
        #     user = None
        user = self.get_user(request)

        if user is not None and user.is_authenticated:
            # 用户已登录，在Redis中保存
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()

            # 记录购物车商品数量
            # hincrby(hash, key, value) {'sku_id_1': 1}
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # 记录购物车的勾选项
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            """
            用户未登录， 在cookie中保存
            使用pickle序列化购物车数据，pickle操作的是bytes类型
            """
            # 获取cookie里的cart数据
            cart = request.COOKIES.get('cart', None)

            if cart is not None:  # 如果不为空 则说明其内有数据
                '''
                # 把str类型转换为bytes类型的字符串
                cart_str_bytes = cart.encode()
                # 把bytes类型字符串转换为bytes类型
                cart_bytes = base64.b64decode(cart_str_bytes)
                # 把bytes类型转换成Python的dict
                cart_dict = pickle.loads(cart_bytes)
                '''
                cart_dict = pickle.loads(base64.b64decode(cart.encode()))
            else:
                # 如果为空 则只需创建空字典即可
                cart_dict = {}
        # 在字典中获取当前sku_id
        sku = cart_dict.get(sku_id)
        if sku:  # 如果sku有值
            count += int(sku.get('count'))  # 将键count加1即可
        # 组装当前sku_id的字典
        cart_dict[sku_id] = {
            'count': count,
            "selected": selected
        }
        '''
        # 反序列化
        # 字典 --> bytes
        cookie_cart_bytes = pickle.dumps(cart_dict)
        # bytes --> bytes类型字符串
        cookie_cart_bytes_str = base64.b64encode(cookie_cart_bytes)
        # bytes类型字符串 --> 字符串
        cookie_cart_str = cookie_cart_bytes_str.decode()
        '''
        cookie_cart = base64.b64encode(pickle.dumps(cart_dict)).decode()

        # 设置返回头
        response = Response(serializer.data, status=status.HTTP_201_CREATED)

        # 设置购物车的cookie
        # 需要设置有效期，否则是临时cookie
        response.set_cookie('cart', cookie_cart, max_age=CART_COOKIE_EXPIRES)
        return response

    def put(self, request):
        """
        修改购物车数据
        """
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        # try:
        #     user = request.user
        # except Exception:
        #     user = None
        user = self.get_user(request)

        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hset('cart_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data)
        else:
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

            cart[sku_id] = {
                'count': count,
                'selected': selected
            }
            cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()

            response = Response(serializer.data)

            response.set_cookie('cart', cookie_cart, max_age=CART_COOKIE_EXPIRES)
            return response

    def delete(self, request):
        """
        删除购物车数据
        """
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']

        # try:
        #     user = request.user
        # except Exception:
        #     user = None
        user = self.get_user(request)

        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id, sku_id)
            pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT)

            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                if sku_id in cart:
                    del cart[sku_id]
                    cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                    response.set_cookie('cart', cookie_cart, max_age=CART_COOKIE_EXPIRES)
            return response

