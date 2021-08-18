from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
# Create your views here.
from .serializers import AreasSerializer, AreaSubsSerializer
from .models import Area


class AreasView(ListAPIView):
    serializer_class = AreasSerializer
    queryset = Area.objects.filter(parent__isnull=True)


class AreaSubsView(RetrieveAPIView):
    serializer_class = AreaSubsSerializer
    queryset = Area.objects.all()


class AreaViewSet(ReadOnlyModelViewSet):
    def get_queryset(self):
        if self.action == "list":
            return Area.objects.filter(parent__isnull=True)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AreasSerializer
        else:
            return AreaSubsSerializer
