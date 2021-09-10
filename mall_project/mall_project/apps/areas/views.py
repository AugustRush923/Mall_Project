from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin
# Create your views here.
from .serializers import AreasSerializer, AreaSubsSerializer
from .models import Area


# class view形式
class AreasView(ListAPIView):
    serializer_class = AreasSerializer
    queryset = Area.objects.filter(parent__isnull=True)


class AreaSubsView(RetrieveAPIView):
    serializer_class = AreaSubsSerializer
    queryset = Area.objects.all()


# ViewSet形式
class AreaViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    pagination_class = None

    # 根据不同action 返回不同queryset
    def get_queryset(self):
        if self.action == "list":
            # 如果action是list 则查询顶级单位
            return Area.objects.filter(parent__isnull=True).order_by('id')
        elif self.action == "retrieve":
            # 如果action是retrieve， 则查询所有
            return Area.objects.all().order_by('id')

    # 根据不同action，返回不同Serializer
    def get_serializer_class(self):
        if self.action == "list":
            return AreasSerializer
        elif self.action == "retrieve":
            return AreaSubsSerializer
