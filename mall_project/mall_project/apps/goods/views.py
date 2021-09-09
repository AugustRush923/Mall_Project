from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from goods.models import SKU, GoodsCategory
from goods.serializers import ChannelSerializer, CategorySerializer, SKUSerializer

# Create your views here.


class SKUListView(ListAPIView):
    serializer_class = SKUSerializer
    filter_backends = (OrderingFilter,)
    order_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)


class CategoriesView(GenericAPIView):
    queryset = GoodsCategory.objects.all()

    def get(self, request, pk=None):
        # 创建一个字典
        ret = dict(
            cat1='',
            cat2='',
            cat3=''
        )
        # 根据pk获取指定category
        category = self.get_object()
        if category.parent is None:
            # 当parent字段为null 意味第一级
            ret['cat1'] = ChannelSerializer(category.goodschannel_set.all()[0]).data
        elif category.goodscategory_set.count() == 0:
            ret['cat3'] = CategorySerializer(category).data
            cat2 = category.parent
            ret['cat2'] = CategorySerializer(cat2).data
            ret['cat1'] = ChannelSerializer(cat2.parent.goodschannel_set.all()[0]).data
        else:
            ret['cat2'] = CategorySerializer(category).data
            ret['cat1'] = ChannelSerializer(category.parent.goodschannel_set.all()[0]).data
        return Response(ret)
