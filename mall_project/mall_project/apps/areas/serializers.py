from rest_framework import serializers

from .models import Area


class AreasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id', 'name']


class AreaSubsSerializer(serializers.ModelSerializer):
    subs = AreasSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']
