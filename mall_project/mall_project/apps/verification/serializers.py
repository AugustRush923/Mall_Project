from django_redis import get_redis_connection
from rest_framework import serializers


class ImageCodeCheckSerializer(serializers.Serializer):
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        # 获取相应参数
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        # 查询真实图片验证码值
        redis_conn = get_redis_connection('captcha')
        real_image_code = redis_conn.get('img_%s' % image_code_id)
        if not real_image_code:
            raise serializers.ValidationError("图片验证码无效")

        # 删除图片验证码
        redis_conn.delete('img_%s' % image_code_id)

        # 比较图片验证码
        real_image_code = real_image_code.decode()
        if real_image_code.lower() != text.lower():
            raise serializers.ValidationError("图片验证码错误")

        # 判断是否是在60s内
        # GenericAPIView的get_serializer方法在创建序列化器对象时候会补充context属性
        # context属性包含三个值 request   format  view--》类视图对象
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get("send_flag_%s" % mobile)
        if send_flag:
            raise serializers.ValidationError("操作过于频繁，请稍后再试")

        return attrs
