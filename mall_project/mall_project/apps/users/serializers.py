import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from goods.models import SKU
from .models import User, Address

from celery_tasks.send_email.tasks import send_verify_mail


class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label="登录状态token", read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow', 'token']

        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        """检验用户是否同意协议"""
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, data):
        # 判断两次密码
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 判断短信验证码
        redis_conn = get_redis_connection('captcha')
        mobile = data['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if data['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        return data

    def create(self, validated_data):
        """重写create方法，实现密码加密"""
        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 调用django的认证系统加密密码
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        # 补充生成记录登录状态的token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        print(payload)
        token = jwt_encode_handler(payload)
        print(token)
        user.token = token
        # token = api_settings.JWT_ENCODE_HANDLER(api_settings.JWT_PAYLOAD_HANDLER(user))
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'email_active']


class UpdatePasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(label="新密码", write_only=True, min_length=8, max_length=20)
    confirm_password = serializers.CharField(label='确认密码', write_only=True, min_length=8, max_length=20)

    class Meta:
        model = User
        fields = ['id', "password", "new_password", "confirm_password"]

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['password']):
            raise serializers.ValidationError('当前密码不对')
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError('两次密码不一致')
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop('password')
        validated_data.pop('confirm_password')
        print(validated_data)
        instance.set_password(validated_data.get('new_password'))
        instance.save()
        return instance


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']
        extra_kwargs = {
            'email': {
                'required': True,
            }
        }

    def update(self, instance, validated_data):
        print(validated_data)
        instance.email = validated_data.get('email')
        instance.save()

        verify_url = instance.generate_verify_email_url()
        print(verify_url)
        send_verify_mail.delay(instance.email, verify_url)
        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    """
       用户地址序列化器
       """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_delete', 'create_time', 'update_time')

    def validated_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super(UserAddressSerializer, self).create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ('title',)


class AddUsersHistorySerializer(serializers.ModelSerializer):
    """
    添加用户浏览历史序列化器
    """
    sku_id = serializers.IntegerField(label="商品sku编号", min_value=1)

    def validate_sku_id(self, value):
        """
        检验sku-id是否存在
        """
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError("该商品不存在")

        return value

    def create(self, validated_data):
        """
        保存到Redis
        """
        user_id = self.context['request'].user.id
        sku_id = validated_data['sku_id']

        redis_conn = get_redis_connection('history')
        pl = redis_conn.pipline()

        # 移除已经存在的本商品浏览记录
        pl.lrem(f"history_{user_id}", 0, sku_id)
        # 添加新的浏览记录
        pl.lpush(f"history_{user_id}", sku_id)
        # 只保存最多5条记录
        pl.ltrim("history_%s" % user_id, 0, 4)

        pl.excuate()

        return validated_data


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'comments']
