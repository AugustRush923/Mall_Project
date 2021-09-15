import decimal

from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_redis import get_redis_connection
# Create your views here.

from goods.models import SKU
from orders.serializers import OrderSettlementSerializer, SaveOrderSerializer


class OrderSettlementView(APIView):
    """
    订单结算
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        获取
        """
        user = request.user

        # 从购物车中获取用户勾选要结算的商品信息
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)

        cart = {}
        # 把hash中那些勾选商品的sku_id和count取出来包装到一个新字典中
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        # 遍历查询集取出单个模型
        for sku in skus:
            # 给每个模型定义一个count属性
            sku.count = cart[sku.id]

        # 运费
        freight = decimal.Decimal('10.00')

        serializer = OrderSettlementSerializer({'freight': freight, 'skus': skus})
        return Response(serializer.data)


class SaveOrderView(CreateAPIView):
    """
    保存订单
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer
