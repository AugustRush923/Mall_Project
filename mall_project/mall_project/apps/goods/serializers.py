from rest_framework import serializers

from goods.models import GoodsCategory, GoodsChannel


class ChannelSerializer(serializers.ModelSerializer):
    """频道序列化器"""

    category = serializers.StringRelatedField(label="顶级商品分类")

    class Meta:
        model = GoodsChannel
        # exclude = ['id', 'sequence', 'create_time', 'update_time']
        fields = ['category', 'url']


class CategorySerializer(serializers.ModelSerializer):
    """商品品类序列化器"""

    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']
